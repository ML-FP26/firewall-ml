"""Clean the raw firewall CSV, produce the frozen split, and expose load_split().

Owner: A (Bima Satriawan)
Contract: docs/00-shared-contracts.md sections 3.2, 3.3, 3.4
"""

import hashlib
import json
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "firewall.csv"
PROCESSED_DIR = ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Contract constants (§3.3)
# ---------------------------------------------------------------------------

RANDOM_STATE: int = 42
LABEL: str = "action"

# The 11 clean feature names, in the fixed order from §3.2.
FEATURES: list[str] = [
    "source_port",
    "destination_port",
    "nat_source_port",
    "nat_destination_port",
    "bytes",
    "bytes_sent",
    "bytes_received",
    "packets",
    "elapsed_time_sec",
    "pkts_sent",
    "pkts_received",
]

# Column rename map: original UCI header → clean name.
_RENAME: dict[str, str] = {
    "Source Port": "source_port",
    "Destination Port": "destination_port",
    "NAT Source Port": "nat_source_port",
    "NAT Destination Port": "nat_destination_port",
    "Action": "action",
    "Bytes": "bytes",
    "Bytes Sent": "bytes_sent",
    "Bytes Received": "bytes_received",
    "Packets": "packets",
    "Elapsed Time (sec)": "elapsed_time_sec",
    "pkts_sent": "pkts_sent",
    "pkts_received": "pkts_received",
}

# Populated lazily on first call to load_split(); set by _ensure_split().
LABELS: list[str] = []


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    """Return the sha256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _n_conflicting_groups(df: pd.DataFrame) -> int:
    """Count groups of rows with identical features but more than one label.

    A conflicting group means the same 11-feature signature maps to different
    firewall actions — this is label noise, not duplicates.
    """
    grouped = df.groupby(FEATURES)[LABEL].nunique()
    return int((grouped > 1).sum())


def _build_freeze(raw: pd.DataFrame, deduped: pd.DataFrame,
                  train: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Return the freeze.json dict with all required fields."""
    labels = sorted(deduped[LABEL].unique().tolist())
    return {
        "version": 1,
        "frozen_on": date.today().isoformat(),
        "random_state": RANDOM_STATE,
        "test_size": 0.2,
        "n_rows_raw": int(len(raw)),
        "n_rows_after_dedupe": int(len(deduped)),
        "n_conflicting_feature_groups": _n_conflicting_groups(deduped),
        "labels": labels,
        "class_counts_after_dedupe": deduped[LABEL].value_counts().sort_index().to_dict(),
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "class_counts_train": train[LABEL].value_counts().sort_index().to_dict(),
        "class_counts_test": test[LABEL].value_counts().sort_index().to_dict(),
        "sha256": {
            "train.csv": _sha256(PROCESSED_DIR / "train.csv"),
            "test.csv": _sha256(PROCESSED_DIR / "test.csv"),
        },
        "rare_class_policy": "keep_all_4_classes",
    }


def _write_freeze_md(freeze: dict) -> None:
    """Write a human-readable summary of the freeze."""
    lines = [
        "# Data freeze summary",
        "",
        f"Frozen on: {freeze['frozen_on']}  ",
        f"Random state: {freeze['random_state']}  ",
        f"Test size: {freeze['test_size']}  ",
        "",
        "## Row counts",
        "",
        f"| Stage | Rows |",
        f"|---|---|",
        f"| Raw (before dedupe) | {freeze['n_rows_raw']:,} |",
        f"| After removing exact duplicates | {freeze['n_rows_after_dedupe']:,} |",
        f"| Removed as duplicates | {freeze['n_rows_raw'] - freeze['n_rows_after_dedupe']:,} |",
        f"| Train (80 %) | {freeze['n_train']:,} |",
        f"| Test (20 %) | {freeze['n_test']:,} |",
        "",
        f"Conflicting feature groups (same features, different labels): "
        f"{freeze['n_conflicting_feature_groups']}",
        "",
        "## Class distribution after dedupe",
        "",
        "| Class | After dedupe | Train | Test |",
        "|---|---|---|---|",
    ]
    for label in freeze["labels"]:
        lines.append(
            f"| {label} | {freeze['class_counts_after_dedupe'][label]:,} | "
            f"{freeze['class_counts_train'][label]:,} | "
            f"{freeze['class_counts_test'][label]:,} |"
        )
    lines += [
        "",
        f"Rare-class policy: {freeze['rare_class_policy']}",
        "",
        "## SHA-256 checksums",
        "",
        f"| File | SHA-256 |",
        f"|---|---|",
        f"| train.csv | `{freeze['sha256']['train.csv']}` |",
        f"| test.csv  | `{freeze['sha256']['test.csv']}` |",
    ]
    (PROCESSED_DIR / "FREEZE.md").write_text("\n".join(lines), encoding="utf-8")


def _ensure_split() -> None:
    """Create data/processed/ files if they do not exist yet.

    Call order:
      1. Load raw CSV.
      2. Rename to clean names.
      3. Lower-case the action column (class names come from the data).
      4. Drop exact duplicates (all 12 columns including the label).
      5. Stratified 80/20 split with RANDOM_STATE.
      6. Write train.csv, test.csv, freeze.json, FREEZE.md.
    """
    global LABELS

    train_path = PROCESSED_DIR / "train.csv"
    test_path = PROCESSED_DIR / "test.csv"
    freeze_path = PROCESSED_DIR / "freeze.json"

    if train_path.exists() and test_path.exists() and freeze_path.exists():
        # Already frozen: just populate LABELS from freeze.json.
        freeze = json.loads(freeze_path.read_text())
        LABELS[:] = sorted(freeze["labels"])
        return

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load raw.
    raw = pd.read_csv(RAW_PATH)
    n_raw = len(raw)

    # 2. Rename columns.
    raw = raw.rename(columns=_RENAME)

    # 3. Lower-case the action column.
    raw[LABEL] = raw[LABEL].str.lower()

    # 4. Remove exact duplicates (all 12 columns).
    deduped = raw.drop_duplicates().reset_index(drop=True)

    # 5. Stratified 80/20 split.
    X = deduped[FEATURES]
    y = deduped[LABEL]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # 6. Write CSV files (features + label, clean names).
    all_cols = FEATURES + [LABEL]
    train_df = X_train.copy()
    train_df[LABEL] = y_train.values
    test_df = X_test.copy()
    test_df[LABEL] = y_test.values

    train_df[all_cols].to_csv(train_path, index=False)
    test_df[all_cols].to_csv(test_path, index=False)

    # 7. Build and write freeze records.
    freeze = _build_freeze(raw.iloc[:n_raw], deduped, train_df, test_df)
    freeze_path.write_text(json.dumps(freeze, indent=2), encoding="utf-8")
    _write_freeze_md(freeze)

    LABELS[:] = sorted(freeze["labels"])

    print(
        f"Freeze written: {n_raw:,} raw rows → {len(deduped):,} after dedupe "
        f"→ {len(train_df):,} train / {len(test_df):,} test"
    )
    print(f"Labels: {LABELS}")
    if freeze["n_conflicting_feature_groups"] > 0:
        print(
            f"WARNING: {freeze['n_conflicting_feature_groups']} conflicting feature groups "
            "(same features, different labels). Reported but not dropped."
        )


# ---------------------------------------------------------------------------
# Public API  (§3.3)
# ---------------------------------------------------------------------------

def load_split() -> tuple[pd.DataFrame, pd.DataFrame, "pd.Series", "pd.Series"]:
    """Return X_train, X_test, y_train, y_test.

    Raw numeric features (unscaled). Columns == FEATURES, same order in both.
    y_* are strings from LABELS.

    Verifies the sha256 of train.csv and test.csv against freeze.json and
    raises RuntimeError if either file has changed since the freeze.
    """
    global LABELS

    _ensure_split()

    freeze = json.loads((PROCESSED_DIR / "freeze.json").read_text())

    for file_name in ("train.csv", "test.csv"):
        expected = freeze["sha256"][file_name]
        actual = _sha256(PROCESSED_DIR / file_name)
        if actual != expected:
            raise RuntimeError(
                f"{file_name} has changed since the freeze. "
                f"Expected sha256 {expected}, got {actual}. "
                "If this is intentional, re-run data.py to create a new freeze."
            )

    LABELS[:] = sorted(freeze["labels"])

    train = pd.read_csv(PROCESSED_DIR / "train.csv")
    test = pd.read_csv(PROCESSED_DIR / "test.csv")

    X_train = train[FEATURES]
    y_train = train[LABEL]
    X_test = test[FEATURES]
    y_test = test[LABEL]

    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------------------------
# CLI (python -m src.data)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Running as a script forces the split to be created (or confirms it exists).
    _ensure_split()
    from src.data import LABELS as _labels  # re-import to show populated value
    freeze = json.loads((PROCESSED_DIR / "freeze.json").read_text())
    print("\nFreeze summary:")
    print(f"  raw rows         : {freeze['n_rows_raw']:,}")
    print(f"  after dedupe     : {freeze['n_rows_after_dedupe']:,}")
    print(f"  train / test     : {freeze['n_train']:,} / {freeze['n_test']:,}")
    print(f"  conflicting groups: {freeze['n_conflicting_feature_groups']}")
    print(f"  labels           : {freeze['labels']}")
    print(f"  rare-class policy: {freeze['rare_class_policy']}")
