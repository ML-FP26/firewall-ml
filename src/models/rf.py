"""Random Forest classifier model specification.

Owner: B
Contract: docs/00-shared-contracts.md section 5.1
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

NAME: str = "rf"
SEARCH: str = "random"
N_ITER: int = 20

# Hyperparameter search space for tuning via 5-fold CV
PARAM_GRID: dict = {
    "clf__n_estimators": [200, 400],
    "clf__max_depth": [None, 20, 40],
    "clf__min_samples_leaf": [1, 2, 5],
    "clf__max_features": ["sqrt", 0.5],
    "clf__class_weight": [None, "balanced_subsample"],
}


def build_model(**overrides) -> Pipeline:
    """Return an unfitted Pipeline wrapping RandomForestClassifier."""
    clf_kwargs = {
        "random_state": 42,
        "n_jobs": -1,
    }
    clf_kwargs.update(overrides)

    return Pipeline([("clf", RandomForestClassifier(**clf_kwargs))])
