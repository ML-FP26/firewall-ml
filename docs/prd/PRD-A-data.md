# PRD — A (data)

## Your slice in one paragraph
You own everything about the data being trustworthy. Your freeze is the foundation: if the split leaks or changes, every model result is worthless. You also audit the others' pipelines for leakage, write up what the data actually looks like, and later turn the comparison table into the demo chart. Your hardest work comes first, so your later load is lighter.

## Tasks

| ID | Task | Needs | Produces | Used by |
|---|---|---|---|---|
| A1 | Quick counts + dataset slide card | `data/raw/firewall.csv` (N1) | `results/counts.json`, `docs/slides/proposal/02-dataset.md` | all proposal cards, A2 |
| A2 | Data freeze | N1, A1 | `src/data.py`, `data/processed/*`, `docs/decisions/rare-class.md` | B2, C2, D2, N2, everyone |
| A3 | Leakage audit | A2, N2, B2, C2, D2, N3 | `reports/leakage_audit.md` | Nafi, the lecturer Q&A |
| A4 | Data findings | A1, A2 | `reports/data_findings.md` | A5, N4 |
| A5 | README section | A1, A2, A4 | `docs/readme/02-data.md` | N5 |
| A6 | Comparison chart + demo card | `results/comparison.csv` (N3) | `figures/comparison.png`, `docs/slides/demo/01-comparison.md` | N6 |
| A7 | Lesson line | your own experience | `docs/lessons/a.md` | N6 |

---

## A1 — Quick counts + dataset slide card

**Inputs:** `data/raw/firewall.csv` with the headers in `00` §3.1.

**Outputs**
- `results/counts.json` per `00` §3.5.
- `docs/slides/proposal/02-dataset.md` (slide-card format, `00` §7). It must state: number of samples, number of features, number of classes with their names, class counts and shares, and an explicit imbalance statement.

**Guarantees**
- Computed on the **raw** file, before any dedupe.
- Every number on the card is copied from `counts.json`.
- Class names come from the data, not from this PRD or the UCI page.

**Done when:** `pytest tests -k counts` passes; the card has all four items the brief asks for (samples, features, classes, imbalance).

**Not your problem:** cleaning decisions (that is A2), models.

---

## A2 — Data freeze

**Inputs:** `data/raw/firewall.csv`, `results/counts.json`.

**Outputs** (all specified in `00` §3)
- `src/data.py` with `RANDOM_STATE`, `FEATURES`, `LABEL`, `LABELS`, `load_split()`.
- `data/processed/train.csv`, `data/processed/test.csv`, `data/processed/freeze.json`, `data/processed/FREEZE.md`.
- `docs/decisions/rare-class.md`: the policy chosen for the rarest class, the class counts after dedupe and in train and test, the reason, and what we report instead (macro metrics, per-class recall).

**Guarantees**
- Exact-duplicate rows (all 12 columns, including the label) are removed **before** the split.
- Stratified 80/20 split, `random_state=42`, same result on every run.
- `train.csv` and `test.csv`: identical columns in identical order, clean names per `00` §3.2, numeric dtypes, no NaNs.
- `freeze.json` filled with real values, including `n_conflicting_feature_groups` (identical features, different label). Reported, **not** silently dropped.
- `load_split()` returns raw unscaled features, recomputes the sha256 of both files and raises `RuntimeError` if they differ from `freeze.json`.
- Once frozen, the files never change. A change means a new `version` in `freeze.json`, an entry in `docs/CONTRACT_CHANGES.md`, and a message to Nafi.
- Default rare-class policy is to keep all classes (D9). Changing it needs Nafi's OK and a written reason.

**Done when**
- `pytest tests -k data` passes.
- From a clean clone, `python -c "from src.data import load_split; print([a.shape for a in load_split()])"` runs.
- The counts in `FREEZE.md` match `counts.json` after the dedupe is accounted for.
- You can explain, without notes, why dedupe comes before the split.

**Not your problem:** scaling (lives in model pipelines), CV (C1), metrics (D1).

**Stop and ask Nafi if**
- any class has fewer than 5 rows in `train.csv` (5-fold CV becomes impossible),
- `n_conflicting_feature_groups` is large enough to put a ceiling on achievable accuracy; report the number so the group can discuss it,
- the raw row count differs from the UCI listing.

---

## A3 — Leakage audit

You are the auditor, so unlike everyone else you **do** read other people's code. Output `reports/leakage_audit.md`: one line per check with `PASS` or `FAIL` and one line of evidence (a command output or `file:line`).

Checks:
1. No row of `test.csv` is identical to any row of `train.csv` (compare row hashes).
2. Dedupe happened before the split (`n_rows_after_dedupe` in `freeze.json` equals train + test rows).
3. `src/runner.py` fits and searches on train only, and calls predict on test exactly once per model.
4. Scaling in `logreg` (and `knn` if present) is a step inside the pipeline, not applied to the data beforehand.
5. `src/compare.py` ranks by CV score, not test score.
6. The test set is not used to choose hyperparameters, variants or the best model anywhere (`runner.py`, `compare.py`, `imbalance_ablation.csv` logic).
7. `load_split()` hash check works: modify a copy of `test.csv` and confirm it raises.
8. No feature column is derived from the label.

**Done when:** all 8 checks have a verdict and evidence; any FAIL has been sent to the owner and Nafi with the evidence.

---

## A4 — Data findings

**Outputs:** `reports/data_findings.md`. Cover, with numbers:
- duplicates removed (count and share) and why they matter,
- conflicting rows (same features, different label),
- skew of the numeric columns (min, median, max; do the byte and packet columns span orders of magnitude?),
- whether `bytes == bytes_sent + bytes_received` and `packets == pkts_sent + pkts_received` hold **exactly** in the data (verify, do not assume),
- which columns are near-constant or look uninformative,
- the class imbalance and what it implies for the metric choice.

**Guarantee:** every claim has a number from `counts.json`, `freeze.json` or a one-line computation shown next to it.
**Done when:** B and D can use it to explain their feature and error results without recomputing.

---

## A5 — README section

`docs/readme/02-data.md`: what is in the data, cleaning, split, imbalance. Numbers copied from `results/counts.json` and `data/processed/freeze.json`. Credit UCI (DOI 10.24432/C5131M, CC BY 4.0) is in Nafi's overview; link to it.

---

## A6 — Comparison chart + demo card

**Inputs:** `results/comparison.csv`. Read nothing else.
**Outputs:** `figures/comparison.png`, `docs/slides/demo/01-comparison.md`.
**Guarantees:** the chart shows CV macro-F1 (mean with std error bars) and test macro-F1 per model, readable at slide size, with labelled axes and models sorted by `rank_by_cv`. The card's table is copied from the CSV.
**Done when:** the card has all 5 headings from `00` §7 and you can say which model ranks first and by how much.

---

## A7 — Lesson line
`docs/lessons/a.md`: one honest lesson from your slice, 2–3 sentences, for the lessons-learned slide.

---

## Know this first

### Concepts
- **What a firewall does:** it sits between a network and the internet and decides, for each connection, what to do. Typical actions: **allow** (let it through), **drop** (silently discard), **deny** (block it, usually with a rejection), **reset-both** (send a reset to both ends so the connection is torn down). These meanings are general networking knowledge; the dataset page does not define them, so check the exact semantics before you present them as fact.
- **Ports:** a port number identifies a service on a machine. Destination port is the *service* being asked for (for example 80 web, 443 secure web, 53 DNS). Source port is usually a random high number picked by the client and carries little meaning.
- **NAT:** the firewall rewrites addresses and ports when traffic crosses the boundary. The NAT port columns are the translated values.
- **Bytes, packets, elapsed time:** how much data moved, in how many chunks, over how long a session.
- **Data leakage:** if the same row appears in both train and test, the model is "tested" on something it already memorised, so the score is inflated. This dataset has duplicate rows, so a random split without dedupe leaks.
- **Stratified split:** keeps each class's share the same in train and test. With a rare class, a plain random split could put almost none in the test set.
- **Class imbalance:** one or more classes are far rarer than others. Accuracy then looks great while the rare class is ignored.

### Likely questions
- **Q: Why remove duplicates?** A: Exact duplicate rows can land on both sides of the split, so the model is scored on rows it has already seen. Removing them first keeps the test honest.
- **Q: Why before the split and not after?** A: After the split, copies are already in both files. The only safe order is dedupe, then split.
- **Q: Why stratified?** A: So the rare class appears in both train and test in the same proportion; otherwise its test score could be based on almost nothing.
- **Q: What did you do about the rare class and why?** A: Read it from `docs/decisions/rare-class.md`, and say why macro metrics and per-class recall are reported alongside accuracy.
- **Q: How do you know there is no leakage?** A: The hash check in `load_split()` plus the 8-point audit in `reports/leakage_audit.md`.

### Explain it without notes
1. What is in one row of the table, in plain words?
2. Why does dedupe come before the split?
3. What does `load_split()` guarantee, and what happens if someone edits `test.csv`?
