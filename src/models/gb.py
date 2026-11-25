"""Gradient boosting model definition and search space."""

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline

NAME = "gb"
PARAM_GRID = {
    "clf__learning_rate": [0.03, 0.1, 0.2],
    "clf__max_iter": [200, 400],
    "clf__max_leaf_nodes": [15, 31, 63],
    "clf__min_samples_leaf": [20, 50],
    "clf__l2_regularization": [0, 1],
}
SEARCH = "random"
N_ITER = 20


def build_model(class_weight=None, **overrides) -> Pipeline:
    """Return an unfitted HistGradientBoosting pipeline with requested overrides."""
    classifier = HistGradientBoostingClassifier(
        random_state=42,
        class_weight=class_weight,
        **overrides,
    )
    return Pipeline([("clf", classifier)])
