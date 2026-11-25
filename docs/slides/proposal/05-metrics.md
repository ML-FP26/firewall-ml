# Metrik Evaluasi
Owner: d
Source files: docs/00-shared-contracts.md,docs/prd/PRD-D-baseline-analysis.md

## On the slide (max 5 bullets)
- Metrik utama: macro-F1, yaitu rata-rata F1 setiap kelas dengan bobot yang setara.
- Laporkan juga accuracy, weighted-F1, balanced accuracy, dan MCC.
- Precision, recall, F1, serta confusion matrix ditampilkan untuk setiap kelas.
- Contoh: prediksi yang dominan pada allow dapat tampak akurat, tetapi mengabaikan reset-both; macro-F1 menampakkan kelemahan tersebut.

## Figure
none

## Say out loud (3-5 sentences)
Akurasi merangkum proporsi prediksi yang benar, tetapi dapat menutupi kegagalan pada kelas yang jarang. Macro-F1 menghitung F1 tiap kelas secara setara sehingga kelas langka tetap berpengaruh. Kami juga melaporkan precision, recall, weighted-F1, balanced accuracy, MCC, dan confusion matrix. Dengan demikian, hasil tidak hanya bergantung pada satu angka keseluruhan.
