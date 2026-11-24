"""Train, tune and evaluate any model in src/models/ the same way.

Order inside run(), and nothing else:
load_split -> check_cv_feasible -> search (or load best_params.json)
-> refit on all train -> predict test once -> evaluate -> write files.

Test data is used only for that single predict call.
"""

import argparse
import importlib
import json
import pkgutil
import platform
import time
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
RANDOM_STATE = 42


def list_models() -> list[str]:
    """Return the sorted names of every module in src/models/."""
    import src.models as models_package

    names = [info.name for info in pkgutil.iter_modules(models_package.__path__)]
    return sorted(name for name in names if not name.startswith("_"))


def load_model_module(name: str):
    """Return the module src.models.<name>, or raise ValueError for an unknown name."""
    if name not in list_models():
        raise ValueError(f"Unknown model '{name}'. Available: {list_models()}")
    return importlib.import_module(f"src.models.{name}")


def to_jsonable(value):
    """Return value with numpy scalars converted to plain Python so json can write it."""
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def make_search(module, model):
    """Return an unfitted GridSearchCV or RandomizedSearchCV for this model module."""
    from src.protocol import SCORING, get_cv

    common = dict(scoring=SCORING, cv=get_cv(), refit=True, n_jobs=-1)
    if module.SEARCH == "random":
        return RandomizedSearchCV(
            model,
            module.PARAM_GRID,
            n_iter=module.N_ITER,
            random_state=RANDOM_STATE,
            **common,
        )
    return GridSearchCV(model, module.PARAM_GRID, **common)


def read_saved_cv(out_dir: Path) -> tuple[float, float]:
    """Return (mean, std) of the best CV row saved in cv_results.csv."""
    cv_results = pd.read_csv(out_dir / "cv_results.csv")
    best_row = cv_results.loc[cv_results["rank_test_score"].idxmin()]
    return float(best_row["mean_test_score"]), float(best_row["std_test_score"])


def fit_with_search(module, X_train, y_train, out_dir: Path):
    """Run the CV search on train, save params and cv_results, return the fitted search."""
    search = make_search(module, module.build_model())
    search.fit(X_train, y_train)
    pd.DataFrame(search.cv_results_).to_csv(out_dir / "cv_results.csv", index=False)
    best_params = to_jsonable(search.best_params_)
    (out_dir / "best_params.json").write_text(json.dumps(best_params, indent=2))
    return search


def fit_with_saved_params(module, X_train, y_train, out_dir: Path):
    """Refit on all train using best_params.json, return (fitted model, best_params)."""
    best_params = json.loads((out_dir / "best_params.json").read_text())
    model = module.build_model().set_params(**best_params)
    model.fit(X_train, y_train)
    return model, best_params


def build_preds_table(model, X_test, y_test, y_pred, labels: list[str]) -> pd.DataFrame:
    """Return the preds.csv table: row_id, y_true, y_pred, proba_<label>..."""
    table = pd.DataFrame(
        {"row_id": range(len(y_test)), "y_true": list(y_test), "y_pred": list(y_pred)}
    )
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_test)
        for position, label in enumerate(model.classes_):
            table[f"proba_{label}"] = probabilities[:, position]
        table = table[["row_id", "y_true", "y_pred"] + [f"proba_{label}" for label in labels]]
    return table


def run(name: str, use_saved_params: bool = False) -> dict:
    """Train and evaluate one model, write results/<name>/*, return the metrics dict.

    fit_seconds is the time to refit on the full train file, in both modes.
    """
    from src.data import load_split, LABELS
    from src.metrics import evaluate, save_metrics
    from src.protocol import N_SPLITS, SCORING, check_cv_feasible

    module = load_model_module(name)
    X_train, X_test, y_train, y_test = load_split()
    check_cv_feasible(y_train)

    out_dir = RESULTS_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    if use_saved_params:
        cv_mean, cv_std = read_saved_cv(out_dir)
        start = time.perf_counter()
        model, best_params = fit_with_saved_params(module, X_train, y_train, out_dir)
        fit_seconds = time.perf_counter() - start
    else:
        search = fit_with_search(module, X_train, y_train, out_dir)
        model = search.best_estimator_
        best_params = to_jsonable(search.best_params_)
        best_index = search.best_index_
        cv_mean = float(search.cv_results_["mean_test_score"][best_index])
        cv_std = float(search.cv_results_["std_test_score"][best_index])
        fit_seconds = float(search.refit_time_)

    y_pred = model.predict(X_test)  # the one and only use of test data
    metrics = {
        "model": name,
        "labels": list(LABELS),
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "cv": {"scoring": SCORING, "n_splits": N_SPLITS, "mean": cv_mean, "std": cv_std},
        "test": evaluate(y_test, y_pred, list(LABELS)),
        "fit_seconds": float(fit_seconds),
        "best_params": best_params,
        "versions": {"python": platform.python_version(), "sklearn": sklearn.__version__},
    }

    save_metrics(metrics, out_dir / "metrics.json")
    preds = build_preds_table(model, X_test, y_test, y_pred, list(LABELS))
    preds.to_csv(out_dir / "preds.csv", index=False)
    joblib.dump(model, out_dir / "model.joblib")
    return metrics


def get_fitted_model(name: str):
    """Return the fitted estimator for this model.

    Loads results/<name>/model.joblib if present. Otherwise refits on the train
    file from best_params.json (test data is not touched).
    """
    out_dir = RESULTS_DIR / name
    model_path = out_dir / "model.joblib"
    if model_path.exists():
        return joblib.load(model_path)

    from src.data import load_split

    module = load_model_module(name)
    X_train, _, y_train, _ = load_split()
    model, _ = fit_with_saved_params(module, X_train, y_train, out_dir)
    joblib.dump(model, model_path)
    return model


def main() -> None:
    """Command line entry: python -m src.runner <name> [--use-saved-params]."""
    parser = argparse.ArgumentParser(description="Train and evaluate one model.")
    parser.add_argument("name", help="model module name in src/models/")
    parser.add_argument("--use-saved-params", action="store_true")
    args = parser.parse_args()

    metrics = run(args.name, use_saved_params=args.use_saved_params)
    print(f"model: {metrics['model']}")
    print(f"cv macro-F1: {metrics['cv']['mean']:.4f} +/- {metrics['cv']['std']:.4f}")
    print(f"test macro-F1: {metrics['test']['macro_f1']:.4f}")
    print(f"files written to results/{metrics['model']}/")


if __name__ == "__main__":
    main()
