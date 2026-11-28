# Fitur Paling Berpengaruh
Owner: b
Source files: results/feature_importance.csv,figures/feature_importance.png

## On the slide (max 5 bullets)
- Tiga fitur paling penting: elapsed_time_sec (0.4094), destination_port (0.3794), dan bytes (0.0539).
- Durasi koneksi (elapsed_time_sec) memisahkan paket yang langsung diblokir (0 detik) dari lalu lintas normal.
- Port tujuan (destination_port) mencerminkan kebijakan firewall berbasis layanan target.
- Permutation importance lebih andal dibanding impurity importance yang bias ke port dengan banyak nilai unik.
- Fitur jumlah paket (packets, pkts_sent, pkts_received) memiliki pengaruh marjinal karena redundan dengan bytes.

## Figure
figures/feature_importance.png

## Say out loud (3-5 sentences)
Analisis permutation importance menunjukkan bahwa durasi koneksi dan port tujuan mendominasi keputusan model. Koneksi yang di-deny atau di-drop hampir selalu memiliki elapsed time nol, sedangkan koneksi yang di-allow memiliki durasi lebih panjang. Pengukuran berbasis permutasi ini lebih objektif daripada impurity importance bawaan pohon keputusan yang sering kali bias terhadap port dengan ribuan nilai unik. Fitur ukuran byte juga penting, sementara jumlah paket cenderung redundan karena berkorelasi langsung dengan ukuran byte.

## If the lecturer asks
Q: Mengapa permutation importance lebih dipilih daripada feature importances bawaan (MDI) Random Forest?
A: MDI bawaan pohon keputusan cenderung melebih-lebihkan fitur numerik dengan kardinalitas tinggi seperti nomor port unik. Permutation importance mengukur langsung penurunan skor macro-F1 pada data uji saat nilai suatu fitur diacak, sehingga merefleksikan pengaruh nyata terhadap generalisasi model.
