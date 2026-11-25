# Skenario Pengujian
Owner: c
Source files: docs/00-shared-contracts.md,docs/prd/PRD-C-boosting.md

## On the slide (max 5 bullets)
- Hapus duplikat persis sebelum data dibagi.
- Bagi data secara stratifikasi menjadi 80% train dan 20% test dengan seed 42.
- Gunakan 5-fold StratifiedKFold pada data train untuk penyetelan model dengan macro-F1.
- Pilih model terbaik berdasarkan rata-rata macro-F1 validasi silang, bukan skor test.
- Setelah model dipasang ulang pada seluruh data train, skor test dihitung satu kali per model.

## Figure
none

## Say out loud (3-5 sentences)
Duplikat persis dihapus sebelum pemisahan agar baris yang sama tidak bocor ke dua bagian data. Data kemudian dibagi secara stratifikasi dengan seed tetap. Penyetelan dilakukan memakai lima lipatan pada data train saja. Data test disimpan hingga model akhir siap dan hanya dinilai sekali, sementara model terbaik dipilih dari skor validasi silang.