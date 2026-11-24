"""One test group per artifact schema in docs/00-shared-contracts.md.

Run a group with:  pytest tests -k data|counts|protocol|metrics|results|comparison|analysis|slides

Naming rules, so a keyword only selects its own group:
- a test name or parametrize id never contains another group's keyword;
- `analysis` and `slides` tests skip when their file is missing, and the
  TestSubmission class (no keyword in its names) fails if anything is missing.
"""

import hashlib
import importlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "firewall.csv"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
REPORTS = ROOT / "reports"
SLIDES = ROOT / "docs" / "slides"

RAW_HEADERS = [
    "Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port",
    "Action", "Bytes", "Bytes Sent", "Bytes Received", "Packets",
    "Elapsed Time (sec)", "pkts_sent", "pkts_received",
]
CLEAN_FEATURES = [
    "source_port", "destination_port", "nat_source_port", "nat_destination_port",
    "bytes", "bytes_sent", "bytes_received", "packets", "elapsed_time_sec",
    "pkts_sent", "pkts_received",
]
FREEZE_KEYS = {
    "version", "frozen_on", "random_state", "test_size", "n_rows_raw",
    "n_rows_after_dedupe", "n_conflicting_feature_groups", "labels",
    "class_counts_after_dedupe", "n_train", "n_test", "class_counts_train",
    "class_counts_test", "sha256", "rare_class_policy",
}
COUNTS_KEYS = {
    "source", "n_rows", "n_columns", "n_features", "label_column", "class_counts",
    "class_share", "n_exact_duplicates", "n_missing_cells", "column_dtypes",
}
METRICS_KEYS = {
    "model", "labels", "n_train", "n_test", "cv", "test", "fit_seconds",
    "best_params", "versions",
}
TEST_BLOCK_KEYS = {
    "accuracy", "macro_f1", "weighted_f1", "balanced_accuracy", "mcc",
    "per_class", "confusion_matrix",
}
PER_CLASS_KEYS = {"precision", "recall", "f1", "support"}
COMPARISON_BASE = [
    "rank_by_cv", "model", "cv_macro_f1_mean", "cv_macro_f1_std", "test_accuracy",
    "test_macro_f1", "test_weighted_f1", "test_balanced_accuracy", "test_mcc",
    "fit_seconds",
]
EXPECTED_CARDS = {
    "proposal/01-title.md": "nafi",
    "proposal/02-dataset.md": "a",
    "proposal/03-method.md": "b",
    "proposal/04-test-scenario.md": "c",
    "proposal/05-metrics.md": "d",
    "demo/01-comparison.md": "a",
    "demo/02-best-model.md": "c",
    "demo/03-influential-features.md": "b",
    "demo/04-where-models-fail.md": "d",
    "demo/05-task-split-lessons.md": "nafi",
}
CARD_HEADINGS = [
    "## On the slide (max 5 bullets)",
    "## Figure",
    "## Say out loud (3-5 sentences)",
    "## If the lecturer asks",
]


# ---------------------------------------------------------------- helpers

def read_json(path: Path) -> dict:
    """Return the parsed json file, failing the test with a clear message if missing."""
    assert path.exists(), f"missing file: {path.relative_to(ROOT)}"
    return json.loads(path.read_text())


def read_csv(path: Path) -> pd.DataFrame:
    """Return the csv as a DataFrame, failing the test if the file is missing."""
    assert path.exists(), f"missing file: {path.relative_to(ROOT)}"
    return pd.read_csv(path)


def skip_unless_exists(path: Path) -> None:
    """Skip the test when the artifact has not been produced yet."""
    if not path.exists():
        pytest.skip(f"{path.relative_to(ROOT)} not produced yet")


def sha256_of(path: Path) -> str:
    """Return the sha256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_names() -> list[str]:
    """Return the names of folders in results/ that contain a metrics.json."""
    return sorted(p.parent.name for p in RESULTS.glob("*/metrics.json"))


def model_module_names() -> list[str]:
    """Return the module names in src/models/ (no leading underscore)."""
    folder = ROOT / "src" / "models"
    return sorted(p.stem for p in folder.glob("*.py") if not p.stem.startswith("_"))


def card_paths() -> list[Path]:
    """Return every slide card that exists under docs/slides/."""
    return sorted(SLIDES.glob("*/*.md"))


def card_id(path: Path) -> str:
    """Return a short test id such as 'proposal-02' (no file words, so no keyword clashes)."""
    return f"{path.parent.name}-{path.stem.split('-')[0]}"


def f1_from_confusion(matrix: np.ndarray) -> np.ndarray:
    """Return per-class F1 computed from a confusion matrix (zero_division = 0)."""
    true_pos = np.diag(matrix).astype(float)
    false_pos = matrix.sum(axis=0) - true_pos
    false_neg = matrix.sum(axis=1) - true_pos
    denominator = 2 * true_pos + false_pos + false_neg
    return np.divide(2 * true_pos, denominator, out=np.zeros_like(true_pos), where=denominator > 0)


# ---------------------------------------------------------------- data (A2)

class TestData:
    def test_data_raw_file_has_original_headers(self):
        headers = list(pd.read_csv(RAW_PATH, nrows=0).columns)
        assert headers == RAW_HEADERS

    def test_data_freeze_json_schema(self):
        freeze = read_json(PROCESSED / "freeze.json")
        assert set(freeze) == FREEZE_KEYS
        assert freeze["version"] >= 1
        assert freeze["random_state"] == 42
        assert freeze["test_size"] == 0.2
        assert set(freeze["sha256"]) == {"train.csv", "test.csv"}

    def test_data_freeze_hashes_match_files(self):
        freeze = read_json(PROCESSED / "freeze.json")
        for file_name, expected in freeze["sha256"].items():
            assert sha256_of(PROCESSED / file_name) == expected, f"{file_name} changed after freeze"

    def test_data_freeze_numbers_are_consistent(self):
        freeze = read_json(PROCESSED / "freeze.json")
        assert freeze["n_train"] + freeze["n_test"] == freeze["n_rows_after_dedupe"]
        assert freeze["n_rows_after_dedupe"] <= freeze["n_rows_raw"]
        for key in ["class_counts_after_dedupe", "class_counts_train", "class_counts_test"]:
            assert sorted(freeze[key]) == sorted(freeze["labels"]), key
        assert sum(freeze["class_counts_train"].values()) == freeze["n_train"]
        assert sum(freeze["class_counts_test"].values()) == freeze["n_test"]

    def test_data_frozen_files_are_clean(self):
        for file_name in ["train.csv", "test.csv"]:
            table = read_csv(PROCESSED / file_name)
            assert list(table.columns) == CLEAN_FEATURES + ["action"], file_name
            assert not table.isna().any().any(), f"{file_name} has NaN"
            assert all(pd.api.types.is_numeric_dtype(table[c]) for c in CLEAN_FEATURES)

    def test_data_load_split_shapes_and_labels(self):
        from src.data import FEATURES, LABEL, LABELS, RANDOM_STATE, load_split

        freeze = read_json(PROCESSED / "freeze.json")
        X_train, X_test, y_train, y_test = load_split()
        assert RANDOM_STATE == 42 and LABEL == "action"
        assert FEATURES == CLEAN_FEATURES
        assert list(X_train.columns) == FEATURES and list(X_test.columns) == FEATURES
        assert LABELS == sorted(LABELS) == sorted(freeze["labels"])
        assert set(y_train) | set(y_test) <= set(LABELS)
        assert (len(X_train), len(X_test)) == (freeze["n_train"], freeze["n_test"])
        assert len(X_train) == len(y_train) and len(X_test) == len(y_test)

    def test_data_load_split_is_unscaled(self):
        from src.data import load_split

        X_train, _, _, _ = load_split()
        assert X_train.max().max() > 1000, "features look scaled; load_split must return raw values"

    def test_data_no_duplicate_rows_across_split(self):
        train = read_csv(PROCESSED / "train.csv")
        test = read_csv(PROCESSED / "test.csv")
        combined = pd.concat([train, test], ignore_index=True)
        assert not combined.duplicated().any(), "exact duplicate rows remain (leakage risk)"

    def test_data_split_is_stratified(self):
        freeze = read_json(PROCESSED / "freeze.json")
        for label, total in freeze["class_counts_after_dedupe"].items():
            if total < 10:
                continue
            test_share = freeze["class_counts_test"][label] / total
            assert abs(test_share - freeze["test_size"]) < 0.02, label

    def test_data_rare_class_decision_recorded_if_changed(self):
        freeze = read_json(PROCESSED / "freeze.json")
        if freeze["rare_class_policy"] != "keep_all_4_classes":
            assert (ROOT / "docs" / "decisions" / "rare-class.md").exists()


# ---------------------------------------------------------------- counts (A1)

class TestCounts:
    def test_counts_json_schema(self):
        counts = read_json(RESULTS / "counts.json")
        assert set(counts) == COUNTS_KEYS
        assert counts["n_columns"] == 12 and counts["n_features"] == 11
        assert counts["label_column"] == "Action"
        assert len(counts["column_dtypes"]) == 12

    def test_counts_are_internally_consistent(self):
        counts = read_json(RESULTS / "counts.json")
        assert sum(counts["class_counts"].values()) == counts["n_rows"]
        assert sum(counts["class_share"].values()) == pytest.approx(1.0, abs=1e-6)
        for label, share in counts["class_share"].items():
            assert share == pytest.approx(counts["class_counts"][label] / counts["n_rows"], abs=1e-6)

    def test_counts_match_the_raw_file(self):
        counts = read_json(RESULTS / "counts.json")
        raw = pd.read_csv(RAW_PATH)
        assert counts["n_rows"] == len(raw)
        assert counts["n_exact_duplicates"] == int(raw.duplicated().sum())
        assert counts["n_missing_cells"] == int(raw.isna().sum().sum())
        raw_counts = raw["Action"].str.lower().value_counts().to_dict()
        assert counts["class_counts"] == raw_counts


# ---------------------------------------------------------------- protocol (C1)

class TestProtocol:
    def test_protocol_constants(self):
        from src.protocol import N_SPLITS, SCORING

        assert N_SPLITS == 5
        assert SCORING == "f1_macro"

    def test_protocol_cv_object(self):
        from sklearn.model_selection import StratifiedKFold
        from src.protocol import get_cv

        cv = get_cv()
        assert isinstance(cv, StratifiedKFold)
        assert cv.n_splits == 5 and cv.shuffle is True and cv.random_state == 42

    def test_protocol_cv_is_repeatable(self):
        from src.protocol import get_cv

        X = pd.DataFrame({"f": range(50)})
        y = pd.Series(["a", "b"] * 25)
        first = [test.tolist() for _, test in get_cv().split(X, y)]
        second = [test.tolist() for _, test in get_cv().split(X, y)]
        assert first == second

    def test_protocol_feasible_check_passes_when_enough_rows(self):
        from src.protocol import check_cv_feasible

        check_cv_feasible(pd.Series(["x"] * 5 + ["y"] * 20))

    def test_protocol_feasible_check_rejects_rare_class(self):
        from src.protocol import check_cv_feasible

        with pytest.raises(ValueError, match=r"class x has 4 < 5 train samples"):
            check_cv_feasible(pd.Series(["x"] * 4 + ["y"] * 20))


# ---------------------------------------------------------------- metrics (D1)

class TestMetrics:
    LABELS = ["a", "b", "c"]

    def test_metrics_evaluate_schema(self):
        from src.metrics import evaluate

        y_true = ["a", "a", "b", "b", "c", "c"]
        result = evaluate(y_true, y_true, self.LABELS)
        assert set(result) == TEST_BLOCK_KEYS
        assert list(result["per_class"]) == self.LABELS
        for values in result["per_class"].values():
            assert set(values) == PER_CLASS_KEYS
        assert result["macro_f1"] == pytest.approx(1.0)
        assert result["accuracy"] == pytest.approx(1.0)

    def test_metrics_class_never_predicted(self):
        from src.metrics import evaluate

        y_true = ["a", "a", "b", "b", "c", "c"]
        y_pred = ["a", "a", "b", "b", "b", "b"]
        result = evaluate(y_true, y_pred, self.LABELS)
        assert result["per_class"]["c"]["recall"] == 0
        assert result["per_class"]["c"]["f1"] == 0
        assert result["per_class"]["b"]["precision"] == pytest.approx(0.5)
        assert result["macro_f1"] == pytest.approx((1.0 + 2 / 3 + 0.0) / 3)
        assert result["accuracy"] > result["macro_f1"]

    def test_metrics_confusion_matrix_orientation(self):
        from src.metrics import evaluate

        y_true = ["a", "a", "b", "c"]
        y_pred = ["a", "b", "b", "c"]
        matrix = evaluate(y_true, y_pred, self.LABELS)["confusion_matrix"]
        assert matrix == [[1, 1, 0], [0, 1, 0], [0, 0, 1]]  # rows = true, columns = predicted

    def test_metrics_evaluate_is_json_safe_and_pure(self, capsys, tmp_path, monkeypatch):
        from src.metrics import evaluate

        monkeypatch.chdir(tmp_path)
        result = evaluate(["a", "b", "c"], ["a", "b", "b"], self.LABELS)
        json.dumps(result)
        assert capsys.readouterr().out == ""
        assert list(tmp_path.iterdir()) == []

    def test_metrics_save_creates_folders_and_indents(self, tmp_path):
        from src.metrics import save_metrics

        target = tmp_path / "deep" / "folder" / "metrics.json"
        save_metrics({"a": 1}, target)
        assert target.read_text() == json.dumps({"a": 1}, indent=2)


# ---------------------------------------------------------------- results (runner outputs + model modules)

class TestResults:
    def test_results_at_least_one_model_has_run(self):
        assert model_names(), "no results/<model>/metrics.json yet; run python -m src.runner <name>"

    @pytest.mark.parametrize("name", model_module_names())
    def test_results_model_module_contract(self, name):
        module = importlib.import_module(f"src.models.{name}")
        assert module.NAME == name
        assert isinstance(module.PARAM_GRID, dict) and module.PARAM_GRID
        assert module.SEARCH in {"grid", "random"}
        if module.SEARCH == "random":
            assert isinstance(module.N_ITER, int) and module.N_ITER > 0
        model = module.build_model()
        params = model.get_params()
        assert set(module.PARAM_GRID) <= set(params), "PARAM_GRID has keys the model does not accept"
        for key, value in params.items():
            if key.endswith("random_state"):
                assert value == 42, f"{key} must be 42"

    @pytest.mark.parametrize("name", model_names())
    def test_results_files_exist(self, name):
        for file_name in ["best_params.json", "cv_results.csv", "metrics.json", "preds.csv"]:
            assert (RESULTS / name / file_name).exists(), f"results/{name}/{file_name} missing"

    @pytest.mark.parametrize("name", model_names())
    def test_results_schema_json(self, name):
        data = read_json(RESULTS / name / "metrics.json")
        freeze = read_json(PROCESSED / "freeze.json")
        assert set(data) == METRICS_KEYS
        assert data["model"] == name
        assert data["labels"] == sorted(freeze["labels"])
        assert (data["n_train"], data["n_test"]) == (freeze["n_train"], freeze["n_test"])
        assert data["cv"]["scoring"] == "f1_macro" and data["cv"]["n_splits"] == 5
        assert {"mean", "std"} <= set(data["cv"])
        assert set(data["test"]) == TEST_BLOCK_KEYS
        assert set(data["versions"]) == {"python", "sklearn"}
        assert data["fit_seconds"] >= 0
        assert data["best_params"] == read_json(RESULTS / name / "best_params.json")

    @pytest.mark.parametrize("name", model_names())
    def test_results_numbers_are_consistent(self, name):
        data = read_json(RESULTS / name / "metrics.json")
        test = data["test"]
        matrix = np.array(test["confusion_matrix"])
        assert matrix.shape == (len(data["labels"]),) * 2
        assert matrix.sum() == data["n_test"]
        supports = [test["per_class"][label]["support"] for label in data["labels"]]
        assert supports == matrix.sum(axis=1).tolist()
        assert test["accuracy"] == pytest.approx(np.trace(matrix) / matrix.sum(), abs=1e-6)
        assert test["macro_f1"] == pytest.approx(f1_from_confusion(matrix).mean(), abs=1e-6)

    @pytest.mark.parametrize("name", model_names())
    def test_results_cv_matches_saved_search(self, name):
        data = read_json(RESULTS / name / "metrics.json")
        cv_results = read_csv(RESULTS / name / "cv_results.csv")
        best = cv_results.loc[cv_results["rank_test_score"].idxmin()]
        assert data["cv"]["mean"] == pytest.approx(best["mean_test_score"], abs=1e-9)
        assert data["cv"]["std"] == pytest.approx(best["std_test_score"], abs=1e-9)

    @pytest.mark.parametrize("name", model_names())
    def test_results_preds_table(self, name):
        from src.data import load_split

        data = read_json(RESULTS / name / "metrics.json")
        preds = read_csv(RESULTS / name / "preds.csv")
        labels = data["labels"]
        assert list(preds.columns) == ["row_id", "y_true", "y_pred"] + [f"proba_{x}" for x in labels]
        assert preds["row_id"].tolist() == list(range(data["n_test"]))
        assert set(preds["y_pred"]) <= set(labels)
        proba = preds[[f"proba_{x}" for x in labels]].to_numpy()
        assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-6)
        _, _, _, y_test = load_split()
        assert preds["y_true"].tolist() == list(y_test), "preds.csv rows are not in test.csv order"


# ---------------------------------------------------------------- comparison (N3)

class TestComparison:
    def test_comparison_columns_and_rows(self):
        table = read_csv(RESULTS / "comparison.csv")
        labels = read_json(PROCESSED / "freeze.json")["labels"]
        assert list(table.columns) == COMPARISON_BASE + [f"recall_{x}" for x in sorted(labels)]
        assert sorted(table["model"]) == model_names()

    def test_comparison_is_ranked_by_cv_not_test(self):
        table = read_csv(RESULTS / "comparison.csv")
        assert table["rank_by_cv"].tolist() == list(range(1, len(table) + 1))
        assert table["cv_macro_f1_mean"].is_monotonic_decreasing

    def test_comparison_values_come_from_saved_json(self):
        table = read_csv(RESULTS / "comparison.csv").set_index("model")
        for name in model_names():
            data = read_json(RESULTS / name / "metrics.json")
            row = table.loc[name]
            assert row["cv_macro_f1_mean"] == pytest.approx(data["cv"]["mean"])
            assert row["test_macro_f1"] == pytest.approx(data["test"]["macro_f1"])
            assert row["fit_seconds"] == pytest.approx(data["fit_seconds"])
            for label in data["labels"]:
                assert row[f"recall_{label}"] == pytest.approx(data["test"]["per_class"][label]["recall"])


# ---------------------------------------------------------------- analysis (B3, C3, D3, A4, A6)

class TestAnalysis:
    def test_analysis_top_features_table(self):
        skip_unless_exists(RESULTS / "feature_importance.csv")
        table = pd.read_csv(RESULTS / "feature_importance.csv")
        assert list(table.columns) == [
            "feature", "impurity_importance", "perm_importance_mean", "perm_importance_std",
        ]
        assert sorted(table["feature"]) == sorted(CLEAN_FEATURES)
        assert table["perm_importance_mean"].is_monotonic_decreasing
        assert (FIGURES / "feature_importance.png").exists()

    def test_analysis_imbalance_ablation_table(self):
        skip_unless_exists(RESULTS / "imbalance_ablation.csv")
        table = pd.read_csv(RESULTS / "imbalance_ablation.csv")
        labels = read_json(PROCESSED / "freeze.json")["labels"]
        base = ["variant", "cv_macro_f1_mean", "cv_macro_f1_std", "test_accuracy", "test_macro_f1"]
        assert list(table.columns) == base + [f"recall_{x}" for x in sorted(labels)]
        assert {"none", "class_weight_balanced"} <= set(table["variant"])
        assert (FIGURES / "imbalance_ablation.png").exists()

    def test_analysis_per_class_table(self):
        skip_unless_exists(RESULTS / "per_class_recall.csv")
        table = pd.read_csv(RESULTS / "per_class_recall.csv")
        assert list(table.columns) == ["model", "label", "precision", "recall", "f1", "support"]
        for name in model_names():
            data = read_json(RESULTS / name / "metrics.json")
            rows = table[table["model"] == name].set_index("label")
            assert sorted(rows.index) == sorted(data["labels"]), name
            for label in data["labels"]:
                assert rows.loc[label, "recall"] == pytest.approx(data["test"]["per_class"][label]["recall"])

    def test_analysis_misclassified_rows(self):
        skip_unless_exists(RESULTS / "misclassified_best.csv")
        table = pd.read_csv(RESULTS / "misclassified_best.csv")
        assert list(table.columns) == ["row_id", "y_true", "y_pred"] + CLEAN_FEATURES
        assert (table["y_true"] != table["y_pred"]).all()
        best = read_csv(RESULTS / "comparison.csv").iloc[0]["model"]
        matrix = np.array(read_json(RESULTS / best / "metrics.json")["test"]["confusion_matrix"])
        assert len(table) == matrix.sum() - np.trace(matrix)

    def test_analysis_confusion_figures_exist_per_model(self):
        names = model_names()
        if not any(FIGURES.glob("confusion_*.png")):
            pytest.skip("figures/confusion_<model>.png not produced yet")
        for name in names:
            assert (FIGURES / f"confusion_{name}.png").exists(), name

    @pytest.mark.parametrize(
        "file_name",
        ["error_analysis.md", "data_findings.md", "leakage_audit.md"],
        ids=["error", "findings", "leakage"],
    )
    def test_analysis_reports_are_not_empty(self, file_name):
        skip_unless_exists(REPORTS / file_name)
        assert len((REPORTS / file_name).read_text().strip()) > 200, f"reports/{file_name} is too short"

    def test_analysis_ranking_chart_exists(self):
        skip_unless_exists(RESULTS / "comparison.csv")
        if not (FIGURES / "comparison.png").exists():
            pytest.skip("figures/comparison.png not produced yet")


# ---------------------------------------------------------------- slides (cards)

class TestSlides:
    @pytest.mark.parametrize("path", card_paths(), ids=card_id)
    def test_slides_card_follows_template(self, path):
        text = path.read_text()
        lines = text.splitlines()
        relative = path.relative_to(SLIDES).as_posix()
        assert relative in EXPECTED_CARDS, f"{relative} is not a card named in the contract"
        assert lines[0].startswith("# ") and len(lines[0]) > 2
        assert lines[1] == f"Owner: {EXPECTED_CARDS[relative]}", "Owner line wrong"
        assert re.match(r"Source files: \S+", lines[2]), "Source files line missing"
        positions = [text.find(heading) for heading in CARD_HEADINGS]
        assert all(p >= 0 for p in positions), "a required heading is missing"
        assert positions == sorted(positions), "headings are out of order"

    @pytest.mark.parametrize("path", card_paths(), ids=card_id)
    def test_slides_card_content_limits(self, path):
        sections = re.split(r"^## ", path.read_text(), flags=re.MULTILINE)[1:]
        body = {s.splitlines()[0]: "\n".join(s.splitlines()[1:]).strip() for s in sections}

        bullets = [l for l in body["On the slide (max 5 bullets)"].splitlines() if l.startswith("- ")]
        assert 1 <= len(bullets) <= 5, f"{len(bullets)} bullets"

        figure = body["Figure"].strip()
        assert figure == "none" or (ROOT / figure).exists(), f"figure not found: {figure}"

        spoken = body["Say out loud (3-5 sentences)"]
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", spoken) if s.strip()]
        assert 3 <= len(sentences) <= 5, f"{len(sentences)} sentences"

        questions = body["If the lecturer asks"]
        assert "Q:" in questions and "A:" in questions


# ---------------------------------------------------------------- submission (N7, no group keyword)

class TestSubmission:
    def test_all_expected_cards_present(self):
        missing = [name for name in EXPECTED_CARDS if not (SLIDES / name).exists()]
        assert not missing, f"missing cards: {missing}"

    def test_at_least_three_models_have_outputs(self):
        assert len(model_names()) >= 3, f"only {model_names()} have results"

    def test_every_expected_output_file_is_present(self):
        expected = [
            RESULTS / "counts.json", RESULTS / "comparison.csv",
            RESULTS / "feature_importance.csv", RESULTS / "imbalance_ablation.csv",
            RESULTS / "per_class_recall.csv", RESULTS / "misclassified_best.csv",
            REPORTS / "leakage_audit.md", REPORTS / "data_findings.md",
            REPORTS / "error_analysis.md", FIGURES / "comparison.png",
            FIGURES / "feature_importance.png", FIGURES / "imbalance_ablation.png",
            FIGURES / "flowchart.png", ROOT / "README.md",
            ROOT / "notebooks" / "final_project.ipynb",
        ]
        missing = [str(p.relative_to(ROOT)) for p in expected if not p.exists()]
        assert not missing, f"missing: {missing}"

    def test_model_cards_present(self):
        missing = [n for n in ["rf", "gb", "logreg"] if not (ROOT / "docs" / "model-cards" / f"{n}.md").exists()]
        assert not missing, f"missing model cards: {missing}"

    def test_joblib_files_are_gitignored(self):
        assert "*.joblib" in (ROOT / ".gitignore").read_text().splitlines()
