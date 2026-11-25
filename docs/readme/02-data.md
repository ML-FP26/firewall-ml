## Data

Owner: A (Bima Satriawan)
Sources: `results/counts.json`, `data/processed/freeze.json`

### Dataset

UCI Machine Learning Repository — *Internet Firewall Data* (id 542), DOI [10.24432/C5131M](https://doi.org/10.24432/C5131M), CC BY 4.0. See the overview section for the full credit.

Each row is one network connection record captured by a firewall. The firewall inspects the connection and assigns one of four actions: **allow**, **deny**, **drop**, or **reset-both**. Our task is to predict that action from the 11 numeric columns that describe the connection.

### What is in the data

| Property | Value |
|---|---|
| Raw rows | 65,532 |
| Columns | 12 (11 features + 1 label) |
| Features | All integer: source/destination ports, NAT ports, byte counts, packet counts, elapsed time |
| Label column | `Action` (one of: allow, deny, drop, reset-both) |
| Missing cells | 0 |
| Exact duplicate rows | 8,362 (12.76 %) |

Class distribution in the raw file (from `results/counts.json`):

| Class | Count | Share |
|---|---|---|
| allow | 37,640 | 57.44 % |
| deny | 14,987 | 22.87 % |
| drop | 12,851 | 19.61 % |
| reset-both | 54 | 0.08 % |

`reset-both` is extremely rare. For this reason **macro-F1** is the primary metric: it weights every class equally, so the model cannot hide poor performance on the rare class behind overall accuracy.

### Cleaning and split

Steps, in this exact order (from `data/processed/freeze.json`):

1. **Remove exact duplicates.** 8,362 rows with identical values in all 12 columns are removed before the split. Without this step, copies of test rows could appear in training, inflating the score.
2. **Stratified 80/20 split.** `random_state=42`. Stratification keeps each class's proportion the same in train and test. After dedupe: 57,170 rows → **45,736 train / 11,434 test**.
3. **Freeze.** The resulting `train.csv` and `test.csv` are written once and their SHA-256 checksums stored in `freeze.json`. `load_split()` verifies the checksums on every load and raises an error if either file has changed.

9 conflicting feature groups were found (same 11 features, different label). These are retained and reported; they represent a structural limit on achievable accuracy.

### Imbalance note

After dedupe, `reset-both` has 54 rows total (~43 train, ~11 test). The split is CV-feasible (43 ≥ 5 folds), but test-set estimates for this class have high variance. Per-class recall is reported for every model so this is always visible.

For further detail see `reports/data_findings.md`.
