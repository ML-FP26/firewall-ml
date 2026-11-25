# Kartu Model: Gradient Boosting

## Model

Model ini memakai `HistGradientBoostingClassifier`, yang membangun pohon keputusan secara bertahap dan memperbaiki kesalahan dari pohon-pohon sebelumnya. Model pohon dapat menangani pola nonlinier pada fitur jaringan tanpa penskalaan. Seluruh pencarian parameter memakai 5-fold stratified CV pada data train dengan macro-F1.

## Ruang pencarian

Pencarian acak mencoba 20 kombinasi dari ruang berikut:

| Parameter | Nilai yang dicoba | Makna |
|---|---|---|
| `learning_rate` | 0.03, 0.1, 0.2 | Mengatur besar kontribusi setiap tahap boosting. |
| `max_iter` | 200, 400 | Jumlah maksimum tahap boosting. |
| `max_leaf_nodes` | 15, 31, 63 | Membatasi kompleksitas setiap pohon. |
| `min_samples_leaf` | 20, 50 | Mengatur jumlah minimum sampel pada daun pohon. |
| `l2_regularization` | 0, 1 | Mengatur kekuatan regularisasi L2. |

## Parameter terbaik

Nilai berikut disalin dari `results/gb/best_params.json`:

| Parameter | Nilai |
|---|---:|
| `clf__learning_rate` | 0.03 |
| `clf__max_iter` | 400 |
| `clf__max_leaf_nodes` | 31 |
| `clf__min_samples_leaf` | 50 |
| `clf__l2_regularization` | 0 |

## Hasil

Angka berikut disalin dari `results/gb/metrics.json`.

| Ukuran | Nilai |
|---|---:|
| Baris train / test | 45.736 / 11.434 |
| CV macro-F1, rerata ± simpangan baku | 0.8465387574846016 ± 0.03253838913454662 |
| Test accuracy | 0.9985132062270422 |
| Test macro-F1 | 0.8252466995959529 |

Recall per kelas pada test:

| Kelas | Recall | Support |
|---|---:|---:|
| allow | 1.0 | 7.488 |
| deny | 0.9950248756218906 | 1.608 |
| drop | 1.0 | 2.327 |
| reset-both | 0.18181818181818182 | 11 |

## Keterbatasan

Model masih kesulitan mengenali kelas `reset-both`: recall test rendah pada jumlah sampel yang sedikit. Nilai accuracy yang tinggi tidak menggambarkan kelemahan tersebut; macro-F1 dan recall per kelas memberi gambaran yang lebih seimbang.
