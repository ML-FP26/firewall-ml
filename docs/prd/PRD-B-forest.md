# PRD — B (Random Forest)

## Your slice in one paragraph
You own the Random Forest model, the "which features matter" analysis, and the method slide with the pipeline flowchart. You plug into the shared runner, so you never write splitting, CV or metric code. You supply the model definition and its search space, then you analyse what the trained forest relies on.

## Tasks

| ID | Task | Needs | Produces | Used by |
|---|---|---|---|---|
| B1 | Method slide card + flowchart | decisions D1–D9 in `00` | `docs/slides/proposal/03-method.md`, `figures/flowchart.png` | N6 |
| B2 | Random Forest model | A2, C1, D1, N2 | `src/models/rf.py`, `results/rf/*`, `docs/model-cards/rf.md` | N3, D3, B3 |
| B3 | Top features | B2 | `results/feature_importance.csv`, `figures/feature_importance.png` | B5, N4 |
| B4 | README section | B2, B3 | `docs/readme/03-method.md` | N5 |
| B5 | Influential-features demo card | B3 | `docs/slides/demo/03-influential-features.md` | N6 |
| B6 | Lesson line | your experience | `docs/lessons/b.md` | N6 |

---

## B1 — Method slide card + flowchart

**Inputs:** the locked decisions D1–D9 in `00-shared-contracts.md`. No model results needed.

**Outputs**
- `docs/slides/proposal/03-method.md`: the three models (Random Forest, Gradient Boosting, Logistic Regression) with one line on why each, and the flowchart.
- `figures/flowchart.png`: raw table → remove duplicates → stratified 80/20 split → train: 5-fold CV tuning of each model → refit → test scored once → metrics → comparison → analysis (features, imbalance, errors). Draw it in any tool (draw.io, Mermaid exported to png).

**Guarantees:** the flowchart matches D4, D5 and D8 exactly (dedupe before split, CV on train only, test scored once, best model chosen by CV). The card names at least 3 models and says none are deep learning.

**Done when:** a person who has not read the PRDs can follow the flowchart, and `pytest tests -k slides` passes for this card.

---

## B2 — Random Forest model

**Inputs (you may rely on these, nothing else)**
- `from src.data import load_split` (A2), `from src.protocol import get_cv` (C1), `from src.metrics import evaluate` (D1), `python -m src.runner <name>` (N2).

**Outputs**
- `src/models/rf.py` per `00` §5.1: `NAME = "rf"`, `PARAM_GRID`, `SEARCH`, `N_ITER`, `build_model(**overrides)`.
- `results/rf/` produced by `python -m src.runner rf` (files listed in `00` §5.2).
- `docs/model-cards/rf.md` per `00` §6.5: what it is, why it fits this data, the search space, best params, CV and test numbers copied from `results/rf/metrics.json`, one honest weakness.

**Guarantees**
- `build_model()` returns an unfitted `Pipeline([("clf", RandomForestClassifier(random_state=42, n_jobs=-1))])`. No scaler (trees do not need one). Parameter names in `PARAM_GRID` use the prefix `clf__`.
- `class_weight` is accepted through `overrides`.
- Search space is declared as data in `PARAM_GRID`, not buried in code. Suggested starting space: `n_estimators` [200, 400], `max_depth` [None, 20, 40], `min_samples_leaf` [1, 2, 5], `max_features` ["sqrt", 0.5], `class_weight` [None, "balanced_subsample"]. With `SEARCH = "random"` and `N_ITER = 20` this stays cheap; adjust if you have a reason and write the reason in the model card.
- Nothing in your file reads the test set or the raw data.

**Done when**
- `python -m src.runner rf` finishes and `pytest tests -k "results"` passes for `rf`.
- The model card numbers match `results/rf/metrics.json`.
- You can say, without notes, what each hyperparameter you searched does.

**Not your problem:** how the data was split or cleaned, how CV folds are made, how metrics are computed.

**Stop and ask Nafi if** the runner cannot run your model (error inside `runner.py`), or search time is unreasonable on your machine.

---

## B3 — Top features

**Inputs:** `get_fitted_model("rf")` (N2) and `load_split()` (A2).

**Outputs:** `results/feature_importance.csv` per `00` §6.2 (`feature, impurity_importance, perm_importance_mean, perm_importance_std`) and `figures/feature_importance.png`.

**Guarantees**
- `impurity_importance` comes from the fitted forest; `perm_importance_mean/std` from permutation importance on the **test** set with `scoring="f1_macro"`, `n_repeats=10`, `random_state=42`.
- Sorted by `perm_importance_mean`, descending. The plot shows both measures so disagreement is visible.
- This is analysis only; nothing here feeds back into model selection.

**Done when:** `pytest tests -k analysis` passes; the figure labels every feature by its clean name; you can explain why the two importance measures might disagree.

**Not your problem:** whether other models agree with RF (D3 looks at errors, not at features).

---

## B4 — README section
`docs/readme/03-method.md`: pipeline overview (reuse the flowchart), the shared protocol in two sentences (D4, D5), the RF card, and the feature-importance result. Numbers copied from `results/`.

## B5 — Influential-features demo card
**Inputs:** `results/feature_importance.csv`. Also read `reports/error_analysis.md` (D3 output) so your story and D's story agree; you consume it, you do not edit it.
**Output:** `docs/slides/demo/03-influential-features.md` in slide-card format: the top few features, one sentence on *why* they plausibly matter for a firewall decision, one caveat.
**Done when:** every number on the card is in `feature_importance.csv`.

## B6 — Lesson line
`docs/lessons/b.md`: one honest lesson, 2–3 sentences.

---

## Know this first

### Concepts
- **Decision tree:** a flowchart of yes/no questions on the features ("is destination port < 1024?") that ends in a predicted class. Easy to read, but one tree overfits.
- **Random forest:** many trees, each trained on a random sample of the rows and a random subset of the features at each split, then they vote. Averaging many different trees reduces overfitting. This is called **bagging**.
- **Why no scaling:** trees split on thresholds, so the units of a feature do not matter.
- **Key hyperparameters:** `n_estimators` (number of trees), `max_depth` (how deep each tree can grow), `min_samples_leaf` (smallest allowed leaf, a smoothness knob), `max_features` (how many features each split may consider), `class_weight` (how much to care about rare classes).
- **Impurity importance:** how much each feature reduced "mixedness" across the forest. Fast, but it can favour features with many distinct values.
- **Permutation importance:** shuffle one feature on the test set and see how much the score drops. Slower but measures the real effect on predictions.
- **Correlated features:** if two features carry the same information, importance can be split between them, so each looks less important than it really is.

### Likely questions
- **Q: Why a random forest for this data?** A: Mixed-scale numeric columns, no scaling needed, strong default performance, and it handles non-linear rules such as "this port range plus this size means block".
- **Q: Why do the two importance measures differ?** A: Impurity importance is computed from training splits and can favour high-cardinality features; permutation importance measures damage to test predictions. Disagreement is a signal to trust permutation more.
- **Q: Which feature matters most and why?** A: Read from `feature_importance.csv`; relate it to the firewall's policy (ports identify services, so port-based rules are plausible).
- **Q: How did you tune it without touching the test set?** A: 5-fold stratified CV on the train file, scored with macro-F1; the test set is scored once after the final refit.
- **Q: What is `max_features` for?** A: It forces trees to look at different features, which decorrelates them and makes the averaged forest stronger.

### Explain it without notes
1. How does a random forest make a prediction, and why is it better than one tree?
2. Which hyperparameters did you search and what does each do?
3. What is the difference between impurity importance and permutation importance, and which do you trust more?
