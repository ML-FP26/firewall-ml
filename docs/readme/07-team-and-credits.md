## Team and credits

### Who owned what

| Person | Slice | Main outputs |
|---|---|---|
| Muhamad Nafi' Mulyo | Captain | repo, `src/runner.py`, `src/compare.py`, tests, notebook, README, slide assembly |
| Bima Satriawan | A: data | `src/data.py`, data freeze, `results/counts.json`, leakage audit, data findings |
| Ahmad Zaki Fauzan Nabil | B: Random Forest | `src/models/rf.py`, feature importance, RF model card, method slide |
| Muhammad Nazwar Fakhrurrozy | C: protocol and boosting | `src/protocol.py`, `src/models/gb.py`, imbalance test, GB model card |
| Rayyan Binar Ramadhan | D: baseline and errors | `src/metrics.py`, `src/models/logreg.py`, error analysis, baseline model card |

Each person worked on their own branch and opened a pull request to `main`. The captain reviewed and merged. Work between people passes only through the files and functions defined in `docs/00-shared-contracts.md`.

### Lessons learned

<!-- TODO(nafi): fill from docs/lessons/*.md once each person has written theirs. -->

### How AI was used

Claude Code scaffolded the code and documents from the written specifications in `docs/prd/`. Each member reviewed, ran and can explain their own slice, and the tests in `tests/` check that every part meets its contract.

### References

- UCI Machine Learning Repository, *Internet Firewall Data* (id 542). DOI 10.24432/C5131M. CC BY 4.0.
- Pedregosa et al., *Scikit-learn: Machine Learning in Python*, Journal of Machine Learning Research 12, 2011.
