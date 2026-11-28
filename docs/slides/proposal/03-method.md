# Metode dan Model
Owner: b
Source files: docs/00-shared-contracts.md,docs/prd/PRD-B-forest.md

## On the slide (max 5 bullets)
- Random Forest menangkap pola nonlinier melalui gabungan banyak pohon keputusan.
- HistGradientBoosting membangun pohon bertahap untuk memperbaiki kesalahan sebelumnya secara efisien.
- Logistic Regression menjadi baseline yang sederhana dan mudah ditafsirkan.
- Seluruh model menggunakan pembelajaran mesin klasik; tidak ada deep learning.
- Model terbaik dipilih dari rerata macro-F1 CV; skor test dihitung sekali per model setelah refit.

## Figure
figures/flowchart.png

## Say out loud (3-5 sentences)
Kami membandingkan tiga model dengan karakteristik yang berbeda. Random Forest menggabungkan banyak pohon, sedangkan HistGradientBoosting membangun pohon secara bertahap. Logistic Regression menjadi pembanding linear yang sederhana. Semua model mengikuti alur validasi yang sama agar perbandingannya adil.

## If the lecturer asks
Q: Mengapa tidak menggunakan deep learning untuk data ini?
A: Dataset ini berupa data tabular dengan 11 fitur numerik di mana model ensemble berbasis pohon seperti Random Forest dan Gradient Boosting lebih unggul, efisien dilatih, serta mudah dianalisis tanpa kebutuhan komputasi besar.


