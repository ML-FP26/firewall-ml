"""Build results/comparison.csv from every results/<model>/metrics.json."""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
OUTPUT_PATH = RESULTS_DIR / "comparison.csv"

BASE_COLUMNS = [
    "rank_by_cv",
    "model",
    "cv_macro_f1_mean",
    "cv_macro_f1_std",
    "test_accuracy",
    "test_macro_f1",
    "test_weighted_f1",
    "test_balanced_accuracy",
    "test_mcc",
    "fit_seconds",
]


def load_all_metrics() -> list[dict]:
    """Return the parsed metrics.json of every model folder in results/."""
    paths = sorted(RESULTS_DIR.glob("*/metrics.json"))
    if not paths:
        raise FileNotFoundError("No results/*/metrics.json found. Run a model first.")
    return [json.loads(path.read_text()) for path in paths]


def metrics_to_row(metrics: dict) -> dict:
    """Return one comparison row (without rank) for one metrics.json."""
    test = metrics["test"]
    row = {
        "model": metrics["model"],
        "cv_macro_f1_mean": metrics["cv"]["mean"],
        "cv_macro_f1_std": metrics["cv"]["std"],
        "test_accuracy": test["accuracy"],
        "test_macro_f1": test["macro_f1"],
        "test_weighted_f1": test["weighted_f1"],
        "test_balanced_accuracy": test["balanced_accuracy"],
        "test_mcc": test["mcc"],
        "fit_seconds": metrics["fit_seconds"],
    }
    for label in metrics["labels"]:
        row[f"recall_{label}"] = test["per_class"][label]["recall"]
    return row


def build_comparison() -> pd.DataFrame:
    """Return the comparison table, ranked by CV macro-F1 mean (never by test score)."""
    all_metrics = load_all_metrics()
    label_sets = {tuple(metrics["labels"]) for metrics in all_metrics}
    if len(label_sets) != 1:
        raise ValueError(f"Models disagree on labels: {sorted(label_sets)}")
    labels = list(label_sets.pop())

    table = pd.DataFrame([metrics_to_row(metrics) for metrics in all_metrics])
    table = table.sort_values(
        ["cv_macro_f1_mean", "model"], ascending=[False, True]
    ).reset_index(drop=True)
    table.insert(0, "rank_by_cv", range(1, len(table) + 1))
    return table[BASE_COLUMNS + [f"recall_{label}" for label in labels]]


def main() -> None:
    """Write results/comparison.csv and print it."""
    table = build_comparison()
    table.to_csv(OUTPUT_PATH, index=False)
    print(table.to_string(index=False))
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
