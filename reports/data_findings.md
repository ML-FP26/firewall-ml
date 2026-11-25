# Data findings

Owner: A (Bima Satriawan)
Sources: `results/counts.json`, `data/processed/freeze.json`, computed from `data/raw/firewall.csv`

---

## 1. Duplicate rows

| Metric | Value |
|---|---|
| Raw rows | 65,532 |
| Exact duplicate rows (all 12 columns) | 8,362 |
| Share of raw data that is duplicates | 12.76 % |
| Rows after removing duplicates | 57,170 |

**Why they matter:** an exact duplicate can land on both sides of a random train/test split, letting the model be "tested" on a row it already memorised from training. The score is then inflated. Removing duplicates *before* the split prevents this. The 8,362 removed rows are the size of this risk.

---

## 2. Conflicting feature groups

9 groups of rows have identical values for all 11 features but different `action` labels (computed from `data/processed/freeze.json`, `n_conflicting_feature_groups: 9`).

These 9 groups represent **label noise**: the firewall apparently took different actions for identical connection signatures. They are retained (not dropped), because dropping them would silently remove real data. The implication is that perfect classification accuracy is structurally impossible for at least these groups; the ceiling on achievable macro-F1 is slightly below 1.0 for this reason.

---

## 3. Numeric column ranges

All 11 feature columns are integers. Computed on the raw file (before dedupe).

| Column | Min | Median | Mean | Max |
|---|---|---|---|---|
| `source_port` | 0 | 53,776 | 49,392 | 65,534 |
| `destination_port` | 0 | 445 | 10,577 | 65,535 |
| `nat_source_port` | 0 | 8,820 | 19,283 | 65,535 |
| `nat_destination_port` | 0 | 53 | 2,671 | 65,535 |
| `bytes` | 60 | 168 | 97,124 | 1,269,359,015 |
| `bytes_sent` | 60 | 90 | 22,386 | 948,477,220 |
| `bytes_received` | 0 | 79 | 74,738 | 320,881,795 |
| `packets` | 1 | 2 | 103 | 1,036,116 |
| `elapsed_time_sec` | 0 | 15 | 66 | 10,824 |
| `pkts_sent` | 1 | 1 | 41 | 747,520 |
| `pkts_received` | 0 | 1 | 62 | 327,208 |

The byte and packet columns span **several orders of magnitude** (e.g. `bytes`: 60 to 1.27 billion; median 168, mean 97,124 — median is 578× smaller than the mean). This extreme right skew means tree-based models can split sensibly on raw values, but linear models will be dominated by high-volume connections unless they apply a log or standard-score transform inside their pipeline.

Port columns (0–65,535) are uniformly distributed by range but have high cardinality (source_port: 22,724 unique values). The firewall's rules are likely port-based, so these columns are expected to be informative despite high cardinality.

---

## 4. Column relationships

Verified on the raw file:

| Relationship | Holds exactly? |
|---|---|
| `bytes == bytes_sent + bytes_received` | **Yes** (every row) |
| `packets == pkts_sent + pkts_received` | **Yes** (every row) |

This means `bytes` and `packets` are **derived** from the other columns in their group. All six columns are kept as features because tree models may still find the totals useful as direct split points, but the two derived columns carry no extra information beyond what the four component columns already provide. A linear model, in particular, should not expect independent coefficients across the groups.

---

## 5. Near-constant or low-cardinality columns

No column is near-constant. Unique value counts (computed on raw file):

| Column | Unique values |
|---|---|
| `source_port` | 22,724 |
| `destination_port` | 3,273 |
| `nat_source_port` | 29,152 |
| `nat_destination_port` | 2,533 |
| `bytes` | 10,724 |
| `bytes_sent` | 6,683 |
| `bytes_received` | 8,814 |
| `packets` | 1,116 |
| `elapsed_time_sec` | 915 |
| `pkts_sent` | 749 |
| `pkts_received` | 922 |

All columns have enough variation to be potentially informative. No column is a candidate for removal on the grounds of being near-constant.

---

## 6. Class imbalance

Computed on the raw file (before dedupe), from `results/counts.json`:

| Class | Raw count | Raw share |
|---|---|---|
| allow | 37,640 | 57.44 % |
| deny | 14,987 | 22.87 % |
| drop | 12,851 | 19.61 % |
| reset-both | 54 | 0.08 % |

After removing 8,362 duplicates (from `data/processed/freeze.json`):

| Class | After-dedupe count |
|---|---|
| allow | 37,439 |
| deny | 8,042 |
| drop | 11,635 |
| reset-both | 54 |

**Implication for metric choice:** `reset-both` is extremely rare (54 rows, 0.08 % of the raw data, unchanged after dedupe because nearly none of its rows were duplicates). Accuracy would mask a model that never predicts `reset-both` — it could score >99 % accuracy simply by ignoring the class. For this reason the **primary metric is macro-F1**, which gives every class equal weight. Per-class precision, recall and F1 are reported alongside, so the behaviour on `reset-both` is always visible.

**Implication for the split:** stratified splitting keeps `reset-both` in both train and test at approximately its natural proportion. With 54 rows total and a 80/20 split: ~43 train, ~11 test. This is enough for 5-fold CV (`check_cv_feasible()` passes), but the CV estimate for this class will have high variance given the small support.
