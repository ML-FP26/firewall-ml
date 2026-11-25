"""Shared cross-validation protocol for model selection."""

from collections import Counter

from sklearn.model_selection import StratifiedKFold

N_SPLITS: int = 5
SCORING: str = "f1_macro"


def get_cv() -> StratifiedKFold:
    """Return a fresh, reproducible stratified five-fold splitter."""
    return StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=42)


def check_cv_feasible(y_train) -> None:
    """Raise ValueError when a training class cannot appear in every CV fold."""
    class_counts = Counter(y_train)
    for label, count in sorted(class_counts.items(), key=lambda item: str(item[0])):
        if count < N_SPLITS:
            raise ValueError(
                f"class {label} has {count} < {N_SPLITS} train samples"
            )
