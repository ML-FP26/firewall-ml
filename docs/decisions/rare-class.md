# Rare-class decision

Owner: A (Bima Satriawan)
Date: 2026-11-25

## Decision

**Keep all 4 classes.** Default policy `keep_all_4_classes` from decision D9 in `docs/00-shared-contracts.md`.

## Class counts after deduplication

(Source: `data/processed/freeze.json`)

| Class | After-dedupe count | Train (~80 %) | Test (~20 %) |
|---|---|---|---|
| allow | 37,439 | 29,951 | 7,488 |
| deny | 8,042 | 6,434 | 1,608 |
| drop | 11,635 | 9,308 | 2,327 |
| reset-both | 54 | 43 | 11 |

## Reason for keeping reset-both

`reset-both` has only 54 rows (unchanged by dedupe — none of its rows were exact duplicates). With an 80/20 stratified split this gives ~43 training rows.

- **CV feasibility:** 43 ≥ 5, so `check_cv_feasible()` passes. 5-fold stratified CV is possible.
- **Dropping would hide the problem.** Keeping the class and reporting per-class recall makes the model's performance on the rare class explicit. Dropping it would turn a 4-class problem into a 3-class problem and hide the information that reset-both connections exist and need to be handled.
- **CV estimate variance:** With only ~43 training rows and ~11 test rows the CV score and test recall for `reset-both` will have high variance. This is noted in `reports/data_findings.md` and in the analysis.

## What we report instead of relying on accuracy

Because one class is rare, **macro-F1** is the primary metric (every class weighted equally). We also report per-class precision, recall and F1, so the rare-class behaviour is always visible. Accuracy and weighted-F1 are reported but are not used to compare or select models.
