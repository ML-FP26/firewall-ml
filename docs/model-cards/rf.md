# Model Card: Random Forest (`rf`)

Owner: B
Source: `results/rf/metrics.json`, `results/rf/best_params.json`

## 1. Model Description
Random Forest (`RandomForestClassifier`) is an ensemble learning method constructed from a collection of decorrelated decision trees trained on bootstrap samples of the training data. For multiclass classification, predictions are aggregated by majority vote across all individual trees.

## 2. Why It Fits This Data
1. **Handles Skewed Distributions:** Network traffic features like `bytes` and `packets` exhibit extreme right-skew (spanning several orders of magnitude). Decision trees split on monotonic rank thresholds, making them invariant to feature scaling and outliers.
2. **Feature Interactions:** Network firewall decisions typically depend on combinations of ports and packet counts (e.g., specific destination port with zero elapsed time). Tree-based ensembles naturally capture high-order non-linear feature interactions without manual interaction engineering.
3. **No Feature Scaling Required:** Unlike linear models or distance-based methods, tree ensembles work directly on raw numeric integers.

## 3. Search Space
Hyperparameter tuning used `RandomizedSearchCV` with 20 iterations evaluated via 5-fold Stratified Cross-Validation (`random_state=42`, scoring metric: `f1_macro`):

| Parameter | Values Explored |
|---|---|
| `clf__n_estimators` | `[200, 400]` |
| `clf__max_depth` | `[None, 20, 40]` |
| `clf__min_samples_leaf` | `[1, 2, 5]` |
| `clf__max_features` | `["sqrt", 0.5]` |
| `clf__class_weight` | `[None, "balanced_subsample"]` |

## 4. Best Hyperparameters
From `results/rf/best_params.json`:
- `clf__n_estimators`: 200
- `clf__max_depth`: 20
- `clf__min_samples_leaf`: 2
- `clf__max_features`: 0.5
- `clf__class_weight`: `"balanced_subsample"`

## 5. Performance Metrics
Copied directly from `results/rf/metrics.json`:

### Cross-Validation (5-Fold Stratified on Train Set)
- Metric: `f1_macro`
- Mean: `0.865513`
- Standard Deviation: `0.042464`

### Test Set Performance (Evaluated Once on 11,434 Unseen Rows)
- **Accuracy:** `0.998688` (99.87%)
- **Macro-F1:** `0.881812`
- **Weighted-F1:** `0.998546`
- **Balanced Accuracy:** `0.839787`
- **Matthews Correlation Coefficient (MCC):** `0.997427`
- **Fit Time:** `1.35` seconds

### Per-Class Metrics (Test Set)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| `allow` | 0.999866 | 0.999866 | 0.999866 | 7,488 |
| `deny` | 0.995028 | 0.995647 | 0.995337 | 1,608 |
| `drop` | 0.997428 | 1.000000 | 0.998712 | 2,327 |
| `reset-both` | 1.000000 | 0.363636 | 0.533333 | 11 |

### Confusion Matrix (Test Set)
True labels as rows, predicted labels as columns (`allow`, `deny`, `drop`, `reset-both`):

```
[[7487,    1,    0,    0],
 [   1, 1601,    6,    0],
 [   0,    0, 2327,    0],
 [   0,    7,    0,    4]]
```

## 6. Honest Weakness
The model achieves near-perfect performance on the majority classes (`allow`, `deny`, `drop`), but struggles with the extremely rare class `reset-both` (only 11 test samples, 43 train samples):
- **Low Recall on Rare Class:** Recall for `reset-both` is only 36.36% (4 out of 11 correctly identified; 7 samples were misclassified as `deny`).
- Even with `"balanced_subsample"` weighting, the extreme scarcity of `reset-both` (0.09% of data) makes it difficult for decision trees to split reliably without confusing it with `deny` connections that share similar port or packet characteristics.
