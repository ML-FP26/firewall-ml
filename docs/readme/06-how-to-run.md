## How to run

### On your machine

```bash
git clone https://github.com/ML-FP26/firewall-ml.git
cd firewall-ml
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.data_fetch            # downloads data/raw/firewall.csv
python -m src.data               # cleans, deduplicates, and writes data/processed/
```

Verify the data contracts pass:

```bash
pytest tests -k "counts or data"    # counts.json + frozen split checks
```

Train and evaluate each model. Every run writes its files to `results/<model>/`.

```bash
python -m src.runner rf
python -m src.runner gb
python -m src.runner logreg
```

Add `--use-saved-params` to skip the search and refit from the saved `best_params.json`. This is much faster.

Build the comparison table, ranked by cross-validated macro-F1:

```bash
python -m src.compare               # writes results/comparison.csv
```

<!-- TODO(nafi): add the commands for feature importance, the imbalance test and the error analysis once B, C and D define them. -->

### Check everything

```bash
pytest tests                        # all contract tests
pytest tests -k results             # one group: data, counts, protocol, metrics, results, comparison, analysis, slides
```

### Rebuild this README

```bash
python tools/merge_readme.py        # merges docs/readme/*.md into README.md
```

### On Google Colab

Open `notebooks/final_project.ipynb` and run all cells. The first cell clones this repository, installs `requirements.txt` and sets up the path, so no manual steps are needed. Set `RETRAIN_SEARCH = True` in the setup section only if you want the full search instead of the fast refit.
