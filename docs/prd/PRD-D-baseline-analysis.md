# PRD — D (metrics, baseline, error analysis)

## Your slice in one paragraph
You own how everything is scored (`evaluate()`), the simple baseline model, and the error analysis: the "where models fail" story that carries a big share of the analysis grade. Your modeling load is the lightest, so you carry the hardest thinking: why does a model get a class wrong, and what does the data say about it?

## Tasks

| ID | Task | Needs | Produces | Used by |
|---|---|---|---|---|
| D1 | Eval metrics + metrics slide card | decisions D1–D9 | `src/metrics.py`, `docs/slides/proposal/05-metrics.md` | N2, B2, C2, D2 and every result |
| D2 | LogReg baseline | A2, C1, D1, N2 | `src/models/logreg.py`, `results/logreg/*`, `docs/model-cards/logreg.md` | N3, D3 |
| D3 | Error analysis | B2, C2, D2, N3 | `results/per_class_recall.csv`, `results/misclassified_best.csv`, `figures/confusion_*.png`, `reports/error_analysis.md` | D4, D5, B5 |
| D4 | README section | D2, D3 | `docs/readme/05-findings.md` | N5 |
| D5 | Where-models-fail demo card | D3 | `docs/slides/demo/04-where-models-fail.md` | N6 |
| D6 | Lesson line | your experience | `docs/lessons/d.md` | N6 |

---

## D1 — Eval metrics (shared contract)

**Inputs:** locked decision D6 in `00`.

**Outputs**
- `src/metrics.py` exactly per `00` §4.2: `evaluate(y_true, y_pred, labels) -> dict` and `save_metrics(d, path)`.
- `docs/slides/proposal/05-metrics.md`: which metrics, and why macro-F1 is primary, in slide-card format.

**Guarantees**
- `evaluate()` returns exactly the `"test"` block of `metrics.json` (`00` §5.2): `accuracy, macro_f1, weighted_f1, balanced_accuracy, mcc, per_class{precision,recall,f1,support}, confusion_matrix`.
- Pure function: no file IO, no printing, no global state.
- `labels` fixes the order of `per_class` keys and the confusion-matrix rows and columns, even if a class never appears in `y_pred`. Missing predictions give `0` (not a crash, not NaN): use `zero_division=0`.
- The confusion matrix is a plain list of lists of ints (JSON-safe).

**Done when:** `pytest tests -k metrics` passes, including a case where one class is never predicted; the card explains accuracy versus macro-F1 in one example.

**This is a blocker task:** the runner and every model need it.

**Not your problem:** where predictions come from.

---

## D2 — LogReg baseline

**Inputs (rely on these only):** `load_split()` (A2), `get_cv()` (C1), your `evaluate()` (D1), `python -m src.runner <name>` (N2).

**Outputs**
- `src/models/logreg.py` per `00` §5.1: `NAME = "logreg"`, `PARAM_GRID`, `SEARCH`, `build_model(**overrides)`.
- `results/logreg/` from `python -m src.runner logreg`.
- `docs/model-cards/logreg.md`.

**Guarantees**
- `build_model()` returns an unfitted `Pipeline` whose steps are, in order: a scaler (`StandardScaler`), then `LogisticRegression(max_iter=2000, random_state=42)` named `clf`. Scaling is inside the pipeline, so it is fit on training folds only.
- Optionally add a `log1p` transform of the byte, packet and time columns **inside** the pipeline (they are heavily skewed) and say so in the model card. It is your modeling choice, allowed by the contract.
- Suggested space: `clf__C` [0.01, 0.1, 1, 10], `clf__class_weight` [None, "balanced"].
- Optional extra: a `knn` module with the same contract; it appears in the comparison automatically. Not required.

**Done when:** `python -m src.runner logreg` finishes; `pytest tests -k results` passes for `logreg`; the card states one honest limitation of a linear model on this data.

**Not your problem:** splitting, CV construction, the other models.

---

## D3 — Error analysis

**Inputs**
- `results/*/preds.csv` and `results/*/metrics.json` for every model.
- `results/comparison.csv` (N3), only to know which model ranks first.
- `load_split()` for the feature values of the misclassified rows.

**Outputs** (schemas in `00` §6.4)
- `results/per_class_recall.csv` (`model, label, precision, recall, f1, support`).
- `results/misclassified_best.csv` (`row_id, y_true, y_pred, <FEATURES...>`) for the CV-best model.
- `figures/confusion_<model>.png`, one per model, row-normalised, with clean axis labels.
- `reports/error_analysis.md`.

**Guarantees**
- The report answers three questions, each with evidence from a file in `results/`:
  1. **Which class do the models get wrong, and how badly?** (per-class recall across models)
  2. **Why?** Compare feature distributions of the misclassified rows with correctly classified rows of the true class and of the predicted class. Say what looks different (or that nothing does, which is a finding too).
  3. **What would help?** One or two concrete, honest suggestions (for example more data for the rare class, a different threshold, a feature that is missing).
- Includes how many test rows each class has, so nobody over-reads a rate based on a handful of rows.
- No number is typed by hand; every figure comes from the files above.
- Nothing here feeds back into model selection.

**Done when:** `pytest tests -k analysis` passes; B and C can read the report and agree with it (B's feature story must not contradict yours); you can explain every confusion-matrix cell you show.

---

## D4 — README section
`docs/readme/05-findings.md`: the baseline card, where the models fail, honest limitations. Numbers from `results/`.

## D5 — Where-models-fail demo card
**Input:** `reports/error_analysis.md` and the confusion figures.
**Output:** `docs/slides/demo/04-where-models-fail.md` in slide-card format: the one confusion matrix that tells the story, the failing class with its test support, one reason, one idea to improve.

## D6 — Lesson line
`docs/lessons/d.md`: one honest lesson, 2–3 sentences.

---

## Know this first

### Concepts
- **Accuracy:** share of predictions that are right. Misleading when one class dominates: a model that always says the most common class scores high and is useless for the rare class.
- **Precision (for a class):** of the rows the model *called* that class, how many really were. High precision means few false alarms.
- **Recall (for a class):** of the rows that *truly are* that class, how many the model found. High recall means few misses.
- **F1:** the harmonic mean of precision and recall, so it is only high when both are.
- **Macro-F1:** the average of the per-class F1 scores, each class counted equally. This is our primary metric because it punishes ignoring the rare class.
- **Weighted-F1:** like macro, but weighted by class size, so large classes dominate.
- **Balanced accuracy:** the average of per-class recall.
- **MCC (Matthews correlation coefficient):** a single number from the whole confusion matrix that stays honest under imbalance; 1 is perfect, 0 is no better than chance.
- **Confusion matrix:** rows are the true class, columns the predicted class; the diagonal is correct, everything else is a specific kind of mistake.
- **Logistic regression:** a linear model that turns a weighted sum of the features into class probabilities. Fast and easy to interpret, but it can only draw straight boundaries, and it needs scaled inputs.
- **Why scaling matters for it:** features on huge scales (bytes) would dominate features on small scales (ports) in the weighted sum.
- **Why a baseline:** it sets a floor. If the fancy models barely beat it, the extra complexity is not earning its keep.

### Likely questions
- **Q: Why not just report accuracy?** A: Because one class is far rarer than the others; a model can score high accuracy while never predicting it. Macro-F1 and per-class recall expose that.
- **Q: What is macro-F1?** A: The average of the F1 for each class with every class counted equally, so the rare class matters as much as the common one.
- **Q: Which class do the models fail on and why?** A: Read it from `reports/error_analysis.md`; give the class, its test support, and the evidence you found.
- **Q: What does the confusion matrix show?** A: Walk through one row: what the true class was and where the model put those rows.
- **Q: Why is logistic regression the baseline?** A: It is simple, fast and linear, so it tells us how much the non-linear models actually add.

### Explain it without notes
1. Give an example where accuracy is high but the model is bad, using our data.
2. Read one row of the confusion matrix out loud.
3. What are precision and recall, and when would you prefer one over the other for a firewall?
