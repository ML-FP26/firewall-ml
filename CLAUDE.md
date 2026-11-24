# CLAUDE.md — standing orders for Claude Code

This repo is a group ML course project (UCI Internet Firewall Data, multiclass classification, classical ML only, no deep learning). Five people each own a slice. You are working for one of them at a time.

## Read first, every session
1. `docs/00-shared-contracts.md` — the contracts. They are law.
2. The PRD for the task you were given (`docs/prd/PRD-<owner>-*.md`).

## Rules
1. **Do only the task you were given.** Produce exactly its Outputs at the exact paths with the exact schemas from the shared contracts.
2. **Only edit paths owned by the person you are working for** (ownership table in `00` §2). If another path needs a change, stop and say who owns it.
3. **Never change a contract silently.** If a signature or schema must change, stop, explain, and propose an entry for `docs/CONTRACT_CHANGES.md`.
4. **Consume outputs only.** Use a dependency through its documented file or function. Do not read or copy another task's internals.
5. **Test discipline.** Never use test-set scores to tune, select, or decide anything. Tune with CV on the train file via `src/protocol.py`. Test is scored once per model, by `src/runner.py`.
6. **No fabricated numbers.** Every number in a doc, card or notebook is read from `results/` or `data/processed/freeze.json`, never typed from memory.
7. **Seeds.** `random_state=42` wherever it is accepted.
8. **Scaling and resampling live inside model pipelines**, so they are fit on training folds only.
9. **Never hard-code class names.** Use `LABELS`.
10. **When done, run the pytest keyword from the task's "Done when"** (`pytest tests -k <keyword>`) and show the result.

## Stop and ask when
- A Guarantee cannot be met (for example a class has fewer than 5 training rows).
- The raw data disagrees with the PRD (row count, headers, class names).
- Two PRDs seem to contradict each other.
- You would need to touch a path you do not own.

State the problem with the actual numbers; do not work around it.

## Style
Plain, readable Python. Small functions. Docstrings that say what a function returns. No clever one-liners. Notebook cells under ~25 lines with a markdown sentence above each section. English for code and docs.
