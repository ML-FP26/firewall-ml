# PRD — Nafi (captain)

## Your slice in one paragraph
You own the skeleton everything plugs into: the repo, the runner that trains any model the same way, the comparison, the notebook, the README merge, and the final submission. You also run Claude Code against these PRDs and review every PR. You write almost no modeling logic, which is why your load is coordination, not concepts. You still have to be able to explain the whole pipeline end to end.

## Tasks

| ID | Task | Needs | Produces | Used by |
|---|---|---|---|---|
| N1 | Repo, env, raw data fetch | nothing | repo, `requirements.txt`, `data/raw/firewall.csv` | A1, A2 |
| N2 | Scaffold: runner, compare, tests, notebook skeleton, merge tool | contracts in `00` | `src/runner.py`, `src/compare.py`, `tests/`, `notebooks/final_project.ipynb`, `tools/merge_readme.py` | B2, C2, D2, everyone's "done" check |
| N3 | Comparison | `results/*/metrics.json` | `results/comparison.csv` | A6, C5, D3, N4 |
| N4 | Notebook polish | N3, B3, C3, D3 | final `notebooks/final_project.ipynb` | N7 |
| N5 | README merge | all `docs/readme/*` | `README.md` | N7 |
| N6 | Slide cards + assembly | all cards | `docs/slides/proposal/01-title.md`, `docs/slides/demo/05-task-split-lessons.md`, the two decks | N7 |
| N7 | Submission check | everything | submission-ready repo | the lecturer |

---

## N1 — Repo, env, raw data fetch

**Inputs:** none.

**Outputs**
- GitHub repo with the layout in `00-shared-contracts.md` §2, `.gitignore` containing `*.joblib`, `__pycache__/`, `.ipynb_checkpoints/`.
- `requirements.txt`: pandas, numpy, scikit-learn>=1.3, matplotlib, seaborn, joblib, ucimlrepo, pytest, jupyter, imbalanced-learn (only used by the optional SMOTE variant).
- `src/data_fetch.py` with `fetch(force: bool = False) -> pathlib.Path`, plus CLI `python -m src.data_fetch [--force]`.
- `data/raw/firewall.csv`: the UCI table, original headers, committed.
- Everyone invited as a collaborator: `gh api -X PUT repos/<owner>/<repo>/collaborators/<username> -f permission=push` (each person must accept the invite).

**Guarantees**
- Uses `fetch_ucirepo(id=542)`, concatenates features and target, writes the original headers exactly as listed in `00` §3.1.
- Fails loudly (non-zero exit, clear message) if the downloaded headers differ from §3.1.
- Does not overwrite an existing raw file unless `--force`.
- Prints the row count. The UCI listing says 65,532; if the download disagrees, tell the group before anyone builds on it.

**Done when:** a clean clone runs `pip install -r requirements.txt && python -m src.data_fetch` and `data/raw/firewall.csv` exists with the 12 headers; all 4 friends can push to a branch.

**Not your problem:** cleaning, renaming, dedupe, splitting (A2).

---

## N2 — Scaffold

**Inputs:** only the signatures in `00-shared-contracts.md` §3.3, §4, §5. You code against the *signatures*. The real `data.py`, `protocol.py`, `metrics.py` arrive from A, C and D.

**Outputs**
1. `src/runner.py` exactly per `00` §5.2: `list_models()`, `run(name, use_saved_params=False)`, `get_fitted_model(name)`, CLI.
2. `src/compare.py` exactly per `00` §6.1, CLI `python -m src.compare`.
3. `tests/test_contracts.py`: one test group per artifact schema in `00`, selectable with `pytest tests -k <keyword>`. Keywords: `data`, `counts`, `protocol`, `metrics`, `results`, `comparison`, `analysis`, `slides`. Each owner's "Done when" runs the keyword for their artifact.
4. `notebooks/final_project.ipynb` skeleton with these sections and nothing else: 0 Setup · 1 Problem and data · 2 Data preparation and split · 3 Evaluation protocol · 4 Models · 5 Comparison · 6 Analysis (features, imbalance, errors) · 7 Conclusion and limitations.
5. `tools/merge_readme.py`: concatenates `docs/readme/*.md` in filename order into `README.md`, and fails if any of the 7 files is missing.
6. `docs/CONTRACT_CHANGES.md` with a header and an empty table.

**Guarantees**
- Runner order is exactly: `load_split()` → `check_cv_feasible()` → search (or load `best_params.json`) → refit on all train → predict test **once** → `evaluate()` → write files. No other use of test data.
- The runner never contains model-specific code; a new module in `src/models/` appears in `list_models()` with no runner change.
- Notebook cell 0 is Colab-safe: if `src/` is missing it clones the repo and `cd`s into it, then installs `requirements.txt`. The notebook imports from `src/` and never re-implements logic.
- In section 4 the notebook calls `run(name, use_saved_params=True)` for each model (fast refit from saved params). A boolean `RETRAIN_SEARCH = False` at the top switches to a full search.

**Done when:** `pytest tests -k "data or protocol or metrics"` runs once A2, C1, D1 exist; `python -m src.runner rf` works as soon as B2 exists; the notebook skeleton opens and the setup cell runs on a clean Colab runtime.

**Not your problem:** what the models are or how well they do.

**Stop and ask** if a contract in `00` cannot be implemented as written; propose the change in `CONTRACT_CHANGES.md` first.

---

## N3 — Comparison

**Inputs:** `results/*/metrics.json` (one per model).
**Outputs:** `results/comparison.csv` per `00` §6.1.
**Guarantees:** rows are ranked by `cv_macro_f1_mean`, never by test score; one `recall_<label>` column per label; no number is retyped.
**Done when:** `python -m src.compare` runs and `pytest tests -k comparison` passes.

---

## N4 — Notebook polish

**Inputs:** N3, B3, C3, D3 outputs.
**Outputs:** the final notebook.
**Guarantees**
- Runs top to bottom on a clean Colab runtime with zero errors and no manual steps.
- Every section opens with a 2–3 sentence markdown explanation: what we are doing and why.
- Every figure is loaded from `figures/` or built by a `src/` function; every number comes from `results/`.
- No cell longer than about 25 lines; no commented-out code; no leftover debug prints; consistent naming.
- Section 6 shows feature importance (B3), the imbalance test (C3), and the error analysis (D3) with a short written takeaway each.

**Done when:** a teammate who has never opened the repo runs it cold and gets the same numbers as `results/comparison.csv`.

---

## N5 — README merge

**Inputs:** `docs/readme/01..07-*.md`.
**Outputs:** `README.md` via `python tools/merge_readme.py`.
**Also you write:** `01-overview.md`, `06-how-to-run.md`, `07-team-and-credits.md` (team table from the ownership table, dataset credit to UCI with the DOI and licence, references).
**Done when:** a stranger can go from clone to `results/comparison.csv` using only `06-how-to-run.md`.

---

## N6 — Slide cards and assembly

**Inputs:** all cards under `docs/slides/`.
**Outputs:** `docs/slides/proposal/01-title.md` (title, members, dataset), `docs/slides/demo/05-task-split-lessons.md` (task split from the ownership table plus one lesson per person from `docs/lessons/*.md`), and the two assembled decks.
**Guarantees:** the decks contain only what is on the cards; the proposal deck covers every item the brief lists (title, members, dataset, dataset description with samples/features/classes/imbalance, at least 3 models, flowchart, test scenario, metrics); the demo deck covers comparison, best model and why, interesting findings (influential features, where models fail), task split and lessons.

---

## N7 — Submission check

Deliverables from the brief: the dataset file, the `.ipynb`, and the GitHub documentation link.
- [ ] `pytest tests` passes on a clean clone.
- [ ] README renders on GitHub, links work, and the repo is accessible to the lecturer.
- [ ] Notebook runs cold on Colab.
- [ ] `data/raw/firewall.csv` is in the repo and the UCI credit is in the README.
- [ ] Every person can answer their "Explain it without notes" questions.

---

## How you run Claude Code on a task

Paste this, filling in the task ID:

```
Read CLAUDE.md, docs/00-shared-contracts.md and the PRD for task <ID>.
Implement only that task. Produce exactly its Outputs at the exact paths and
match every schema. Do not edit paths owned by someone else. When done, run
the pytest keyword from the task's "Done when" and show me the result. If a
Guarantee can't be met, stop and tell me with the numbers.
```

## How you review a PR (5 checks)
1. Only the owner's paths changed.
2. The `pytest` keyword for that task passes.
3. No number is typed into a doc; it comes from `results/`.
4. Nothing used test scores to choose anything.
5. If a schema changed, `CONTRACT_CHANGES.md` says so.

---

## Know this first

### Concepts
- **The pipeline in one breath:** raw table → remove duplicate rows → split into train and test once → tune models only with cross-validation on train → score each model on test exactly once → compare → analyse where they fail.
- **Data leakage:** any way test information gets into training. The two sneaky ones here are duplicate rows landing on both sides of a split, and scaling or tuning using the whole dataset.
- **Reproducibility:** fixed seeds, a frozen split with hashes, and results written to files, so anyone gets the same numbers.
- **Contract:** a file or function with a fixed shape. Dependents use only that shape. It is why five people can work in parallel without reading each other's code.
- **Why macro-F1:** accuracy hides a rare class. Macro-F1 averages per-class F1 so every class counts equally.
- **Why choose the best model by CV, not test:** if you pick by test score, the test score is no longer an honest estimate.

### Likely questions
- **Q: How did you split the work?** A: Five vertical slices: data, random forest, boosting plus the evaluation protocol, baseline plus error analysis, and integration. Everyone owns one model or analysis, one docs section and one slide, so the load is balanced and everyone can defend their own part.
- **Q: How do you know the results are not leaked or cherry-picked?** A: Duplicates are removed before the split, tuning uses CV on train only, the test set is scored once per model, and the best model is picked by CV score. A leakage audit in `reports/leakage_audit.md` checks each of these.
- **Q: Did AI write the code?** A: Claude Code scaffolded it from written specifications. Each of us reviewed, ran and can explain our own slice, and the tests in `tests/` check that every part meets its spec.
- **Q: What would you do differently?** A: Answer from `docs/lessons/*.md`.

### Explain it without notes
1. Walk through the pipeline from raw CSV to the comparison table.
2. Why is the test set scored only once, and who enforces that?
3. What does the runner guarantee, and why doesn't any model owner touch splitting or metrics?
