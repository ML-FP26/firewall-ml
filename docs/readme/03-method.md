## Method and Random Forest

Owner: B (Ahmad Zaki Fauzan Nabil)  
Sources: `results/rf/metrics.json`, `results/rf/best_params.json`, `results/feature_importance.csv`

### Pipeline and Shared Protocol

All models follow a shared cross-validation and evaluation pipeline:

1. **Preprocessing and scaling:** Raw numeric features are used directly. Tree-based models do not require feature scaling because decision splits depend on relative ordering, not magnitude.
2. **Hyperparameter search:** Evaluated with 5-fold Stratified Cross-Validation on the training set (45,736 rows) using `f1_macro` as the scoring metric (`random_state=42`).
3. **Refit and evaluation:** After the best hyperparameter set is identified, the model is refit once on the entire training split and evaluated exactly once on the frozen test set (11,434 rows).

### Random Forest Model

Random Forest builds an ensemble of decorrelated decision trees using bootstrap aggregation. It naturally captures non-linear relationships and port-level feature interactions without requiring manual polynomial features.

Hyperparameters were tuned via `RandomizedSearchCV` across 20 iterations:
- `clf__n_estimators`: [200, 400]
- `clf__max_depth`: [None, 20, 40]
- `clf__min_samples_leaf`: [1, 2, 5]
- `clf__max_features`: ["sqrt", 0.5]
- `clf__class_weight`: [None, "balanced_subsample"]

Best parameters found:
- `n_estimators`: 200
- `max_depth`: 20
- `min_samples_leaf`: 2
- `max_features`: 0.5
- `class_weight`: `balanced_subsample`

### Results

Performance recorded in `results/rf/metrics.json`:

| Metric | Score |
|---|---|
| CV Macro-F1 (5-fold mean ± std) | 0.8655 ± 0.0425 |
| Test Accuracy | 99.87 % |
| Test Macro-F1 | 0.8818 |
| Test Weighted-F1 | 0.9985 |
| Test Balanced Accuracy | 0.8398 |
| Test MCC | 0.9974 |

Per-class breakdown on test data:
- `allow`: F1 0.9999 (recall 0.9999, support 7,488)
- `deny`: F1 0.9953 (recall 0.9956, support 1,608)
- `drop`: F1 0.9987 (recall 1.0000, support 2,327)
- `reset-both`: F1 0.5333 (recall 0.3636, precision 1.0000, support 11)

The model achieves near-perfect classification on majority classes. For the rare `reset-both` class (11 test samples), 4 samples are predicted correctly with zero false positives, while 7 samples are misclassified as `deny`.

### Feature Importance

Feature importance was evaluated on the test set using two methods (from `results/feature_importance.csv`):
1. **Mean Decrease in Impurity (MDI):** Built-in Gini importance from tree splits.
2. **Permutation Feature Importance (PFI):** Macro-F1 score drop after shuffling a feature column across 10 repeats (`random_state=42`).

Top features ranked by permutation importance:

| Rank | Feature | Permutation Importance Mean (Macro-F1 Drop) | Impurity Importance |
|:---:|---|:---:|:---:|
| 1 | `elapsed_time_sec` | 0.4094 | 0.1929 |
| 2 | `destination_port` | 0.3794 | 0.3668 |
| 3 | `bytes` | 0.0539 | 0.0859 |
| 4 | `bytes_sent` | 0.0539 | 0.0957 |
| 5 | `source_port` | 0.0475 | 0.1050 |

`elapsed_time_sec` and `destination_port` are the most influential features by a wide margin. Shuffling `elapsed_time_sec` causes a 0.4094 drop in Macro-F1 because blocked connections (`deny` / `drop`) almost always have zero duration, whereas allowed connections stay open. Permutation importance provides a more reliable assessment than MDI, which tends to artificially favor high-cardinality features like raw port numbers.
