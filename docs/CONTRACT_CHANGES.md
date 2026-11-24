# Contract changes

Every change to a contract in `00-shared-contracts.md` is logged here.

| Version | Date | Change | Who is affected | Owner |
|---|---|---|---|---|
| v1.1 | 2026-11-24 | N1 fetch mechanism: `ucimlrepo.fetch_ucirepo(542)` fails with `DatasetNotFoundError`, so `data_fetch.fetch()` downloads UCI's static zip instead. Output file, headers, signature and CLI are unchanged. PRD-nafi N1 wording to be updated. | Nobody downstream | Nafi |
