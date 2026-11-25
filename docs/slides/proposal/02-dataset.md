# Gambaran Dataset
Owner: a
Source files: data/raw/firewall.csv,results/counts.json,docs/00-shared-contracts.md

## On the slide (max 5 bullets)
- Dataset berisi 65.532 sampel dan 11 fitur untuk memprediksi tindakan firewall.
- Terdapat 4 kelas: allow 37.640 (57,4376%), deny 14.987 (22,8697%), drop 12.851 (19,6103%), dan reset-both 54 (0,0824%).
- Distribusi kelas sangat tidak seimbang: kelas reset-both jauh lebih jarang daripada kelas allow.

## Figure
none

## Say out loud (3-5 sentences)
Dataset ini memuat catatan koneksi jaringan beserta tindakan firewall yang diberikan. Setiap sampel memiliki sebelas fitur dan satu label tindakan. Distribusi labelnya tidak seimbang, terutama karena reset-both hanya muncul pada sebagian kecil sampel. Karena itu, evaluasi perlu memperhatikan kinerja setiap kelas, bukan hanya akurasi keseluruhan.

