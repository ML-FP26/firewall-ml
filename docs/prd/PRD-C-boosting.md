# PRD — C (CV protocol, Gradient Boosting)

## Your slice in one paragraph
You own two things: the evaluation protocol everyone shares (the CV object and scoring), and the Gradient Boosting model with its imbalance test. The protocol is a **shared contract**: B, D and the runner all import it, so it has to be finished and exact before models run. After that, you analyse whether handling the imbalance actually helps, and you write the "best model and why" slide.

## Tasks

| ID | Task | Needs | Produces | Used by |
|---|---|---|---|---|
| C1 | Test setup: CV protocol + slide card | decisions D1–D9 | `src/protocol.py`, `docs/slides/proposal/04-test-scenario.md` | N2, B2, C2, D2 |
| C2 | Gradient Boosting model | A2, C1, D1, N2 | `src/models/gb.py`, `results/gb/*`, `docs/model-cards/gb.md` | N3, B-/D-analysis, C3 |
| C3 | Imbalance test | C2 | `results/imbalance_ablation.csv`, `figures/imbalance_ablation.png` | C4, C5 |
| C4 | README section | N3, C2, C3 | `docs/readme/04-results.md` | N5 |
| C5 | Best-model demo card | N3, C3 | `docs/slides/demo/02-best-model.md` | N6 |
| C6 | Lesson line | your experience | `docs/lessons/c.md` | N6 |

---

## C1 — Test setup (shared contract)

**Inputs:** locked decisions D4 (split), D5 (CV), D8 (best-model rule) in `00`.

**Outputs**
- `src/protocol.py` exactly per `00` §4.1: `N_SPLITS = 5`, `SCORING = "f1_macro"`, `get_cv()`, `check_cv_feasible(y_train)`.
- `docs/slides/proposal/04-test-scenario.md`: the test scenario in slide-card format: dedupe, then stratified 80/20 split with a fixed seed, 5-fold stratified CV on train for tuning, the test set scored once, the best model chosen by CV score.

**Guarantees**
- `get_cv()` returns `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. A new object each call, identical behaviour every call.
- `check_cv_feasible()` raises `ValueError("class <X> has <k> < 5 train samples")` when any class has fewer than `N_SPLITS` training rows, and does nothing otherwise.
- The file imports nothing from other `src/` modules, so it can never create an import cycle.

**Done when:** `pytest tests -k protocol` passes; the slide card explains in plain words how the test set is protected from tuning.

**This is a blocker task:** B2, C2, D2 and the runner cannot run until it exists, so finish it before anything else of yours.

**Not your problem:** how the data was split (A2) or what is scored (D1).

---

## C2 — Gradient Boosting model

**Inputs (rely on these only):** `load_split()` (A2), `get_cv()` and `SCORING` (your own C1), `evaluate()` (D1), `python -m src.runner <name>` (N2).

**Outputs**
- `src/models/gb.py` per `00` §5.1: `NAME = "gb"`, `PARAM_GRID`, `SEARCH`, `N_ITER`, `build_model(**overrides)`.
- `results/gb/` from `python -m src.runner gb`.
- `docs/model-cards/gb.md` per `00` §6.5.

**Guarantees**
- `build_model(class_weight=None, **overrides)` returns an unfitted `Pipeline([("clf", HistGradientBoostingClassifier(random_state=42, class_weight=class_weight))])`. `HistGradientBoostingClassifier` is used because the classic `GradientBoostingClassifier` is far slower on tens of thousands of rows. Prefix in `PARAM_GRID`: `clf__`. `class_weight` support needs scikit-learn 1.2 or newer; `requirements.txt` pins `>=1.3`.
- Suggested starting space: `learning_rate` [0.03, 0.1, 0.2], `max_iter` [200, 400], `max_leaf_nodes` [15, 31, 63], `min_samples_leaf` [20, 50], `l2_regularization` [0, 1]. `SEARCH = "random"`, `N_ITER = 20`. Adjust with a written reason in the model card.
- Built-in early stopping, if enabled, uses a validation slice carved from the *training fold*; it never sees test data.

**Done when:** `python -m src.runner gb` finishes; `pytest tests -k results` passes for `gb`; model card numbers equal `results/gb/metrics.json`; you can explain boosting versus bagging without notes.

**Not your problem:** splitting, metrics code, other models.

---

## C3 — Imbalance test

**Inputs:** `build_model` from `src/models/gb.py`, `load_split()`, `get_cv()`, `evaluate()`, and the best params in `results/gb/best_params.json`.

**Outputs:** `results/imbalance_ablation.csv` per `00` §6.3 and `figures/imbalance_ablation.png`.

**Guarantees**
- Variants: `none` and `class_weight_balanced` (required); `smote_in_cv` (optional). If you do SMOTE, it must be a step inside an `imblearn` Pipeline so it is fit on training folds only. Oversampling before CV is a leak and counts as a FAIL in A3's audit.
- Same `get_cv()`, same `evaluate()`, same best params for every variant. The *only* thing that changes is the imbalance handling.
- `recall_<label>` columns for every label, so the effect on the rare class is visible.
- The conclusion is drawn from `cv_macro_f1_mean` and per-class recall. Test numbers are shown but are not used to pick the winner.

**Done when:** `pytest tests -k analysis` passes; the figure shows per-class recall by variant; you can say whether weighting helped the rare class and what it cost the others.

---

## C4 — README section
`docs/readme/04-results.md`: the comparison table (copy from `results/comparison.csv`), the best model and why, the GB card, the imbalance result. Numbers from `results/` only.

## C5 — Best-model demo card

**Inputs:** `results/comparison.csv`, `results/imbalance_ablation.csv`.
**Output:** `docs/slides/demo/02-best-model.md`.
**Guarantees**
- "Best" is the row with `rank_by_cv == 1`.
- If the top two models differ by less than the CV standard deviation, the card says they are **statistically tied** and states the tie-break reason (for example faster, simpler, better recall on the rare class). It does not pretend there is a clear winner.
- The card gives at least one reason beyond a single score (per-class recall, stability across folds, training time).
**Done when:** every number on the card is in a CSV and the tie rule has been checked explicitly.

## C6 — Lesson line
`docs/lessons/c.md`: one honest lesson, 2–3 sentences.

---

## Know this first

### Concepts
- **Train, validation, test:** train fits the model; validation (here, the CV folds inside train) chooses settings; test is touched once at the end to report an honest score.
- **Cross-validation:** split train into 5 parts; train on 4, score on the 1 left out; rotate so every part is scored once; average. It gives a stable estimate without spending the test set.
- **Stratified:** every fold keeps the class proportions, so the rare class appears in every fold.
- **Why shuffle with a fixed seed:** shuffling removes ordering effects; the fixed seed makes it repeatable.
- **Why macro-F1 for tuning:** it weights every class equally, so a model that ignores the rare class cannot win.
- **Boosting vs bagging:** bagging (random forest) trains many trees independently and averages; boosting trains trees one after another, each correcting the errors of the ones before. Boosting can reach higher accuracy but is easier to overfit and has more knobs.
- **Key boosting knobs:** `learning_rate` (step size), `max_iter` (number of trees, trade off against the learning rate), `max_leaf_nodes` and `min_samples_leaf` (tree complexity), `l2_regularization` (penalises extreme leaf values).
- **Class weights:** tell the model that mistakes on the rare class cost more. It usually raises rare-class recall and can lower precision.
- **Oversampling (SMOTE):** invent extra rare-class rows. It must happen inside each training fold; doing it before CV puts near-copies of test rows in training.

### Likely questions
- **Q: How did you stop yourself from tuning on the test set?** A: All tuning uses 5-fold stratified CV on the train file; the test file is scored once per model after the final refit, and the best model is picked by CV score.
- **Q: Why 5 folds?** A: A common balance between a reliable estimate and compute cost; with a rare class, more folds than the class count would be impossible, which `check_cv_feasible()` guards against.
- **Q: Random forest versus gradient boosting?** A: Forest averages independent trees to cut variance; boosting builds trees sequentially to cut bias. Which one wins here is an empirical question answered by CV.
- **Q: Did class weighting help?** A: Read it from `imbalance_ablation.csv`: compare rare-class recall and macro-F1 across variants, and mention any cost to other classes.
- **Q: Why is the best model not just the one with the highest test score?** A: Choosing by test score uses the test set to make a decision, so it stops being an honest estimate.

### Explain it without notes
1. What does `get_cv()` return and why does every model use the same one?
2. How does gradient boosting differ from a random forest?
3. What would go wrong if SMOTE were applied before cross-validation?
