# Tentukan status berdasarkan rasio pengeluaran terhadap pendapatan
def status_rule(row):
    rasio = row["rasio_pengeluaran_pendapatan"]

    if row["total_pendapatan"] == 0:
        return "alert"

    if rasio <= 0.60:
        return "good"

    if rasio <= 0.80:
        return "tip"

    if rasio <= 1.00:
        return "warning"

    return "alert"


# Hitung estimasi penghematan
def estimasi_hemat(nilai, persen):
    if not nilai or nilai <= 0:
        return None

    return int(round(nilai * persen, -3))


# Format angka ke format Rupiah
def format_rupiah(nilai):
    return f"Rp{abs(int(nilai)):,}".replace(",", ".")


#ID unik ke setiap rekomendasi
def add_recommendation_id(recommendations):
    for i, rec in enumerate(recommendations, start=1):
        rec["id"] = f"rec-{i:03d}"

    return recommendations


#Daftar rekomendasi berdasarkan pola pengeluaran
def rekomendasi_rule(row):
    hasil = []

    total_pendapatan = row["total_pendapatan"]
    total_pengeluaran = row["total_pengeluaran"]
    selisih = row["selisih"]
    rasio = row["rasio_pengeluaran_pendapatan"]

    # Cek rasio pengeluaran terhadap pendapatan
    if rasio > 1:
        hasil.append({
            "type": "alert",
            "icon": "🚨",
            "title": "Pengeluaran Melebihi Pendapatan",
            "message": (
                f"Total pengeluaran kamu sudah mencapai "
                f"{rasio * 100:.1f}% dari pendapatan bulanan. "
                f"Coba prioritaskan kebutuhan utama dan kurangi pengeluaran non-esensial."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(total_pengeluaran, 0.10),
            "priority": 1
        })

    elif rasio > 0.85:
        hasil.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Rasio Pengeluaran Tinggi",
            "message": (
                f"Pengeluaran kamu sudah memakai sekitar "
                f"{rasio * 100:.1f}% dari total pendapatan bulan ini. "
                f"Coba mulai membatasi transaksi yang kurang penting."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(total_pengeluaran, 0.08),
            "priority": 2
        })

    elif rasio > 0.70:
        hasil.append({
            "type": "tip",
            "icon": "💡",
            "title": "Pengeluaran Mulai Perlu Dipantau",
            "message": (
                f"Rasio pengeluaran saat ini sekitar "
                f"{rasio * 100:.1f}% dari pendapatan. "
                f"Masih cukup aman, tapi sebaiknya mulai lebih terkontrol."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(total_pengeluaran, 0.05),
            "priority": 5
        })

    # Cek saldo tersisa atau defisit
    if total_pendapatan > 0 and selisih < total_pendapatan * 0.10:

        if selisih < 0:
            message = (
                f"Bulan ini kamu mengalami defisit sekitar "
                f"{format_rupiah(selisih)}. "
                f"Pengeluaran sudah melebihi pendapatan, jadi sebaiknya prioritaskan kebutuhan utama "
                f"dan kurangi pengeluaran non-esensial."
            )

            title = "Keuangan Mengalami Defisit"
            rec_type = "alert"

        else:
            message = (
                f"Sisa saldo bulan ini hanya sekitar "
                f"{format_rupiah(selisih)}. "
                f"Sebaiknya mulai sisihkan dana darurat atau tabungan rutin."
            )

            title = "Sisa Saldo Bulanan Terlalu Kecil"
            rec_type = "warning"

        hasil.append({
            "type": rec_type,
            "icon": "💰",
            "title": title,
            "message": message,
            "category": "tabungan",
            "saving_estimate": estimasi_hemat(total_pendapatan, 0.10),
            "priority": 2
        })

    # Cek pengeluaran makanan
    if row["rasio_makanan"] > 0.20 and row["total_makanan"] >= 300000:
        hasil.append({
            "type": "tip",
            "icon": "🍽️",
            "title": "Pengeluaran Makanan Perlu Dikontrol",
            "message": (
                f"Pengeluaran makanan mencapai sekitar "
                f"{row['rasio_makanan'] * 100:.1f}% "
                f"dari total pengeluaran dengan total "
                f"Rp{int(row['total_makanan']):,}".replace(",", ".")
                + ". Pertimbangkan membuat budget makan harian."
            ),
            "category": "makanan",
            "saving_estimate": estimasi_hemat(row["total_makanan"], 0.15),
            "priority": 3
        })

    # Cek pengeluaran transportasi
    if row["rasio_transportasi"] > 0.15 and row["total_transportasi"] >= 300000:
        hasil.append({
            "type": "tip",
            "icon": "🚗",
            "title": "Biaya Transportasi Cukup Tinggi",
            "message": (
                f"Biaya transportasi bulan ini sekitar "
                f"Rp{int(row['total_transportasi']):,}".replace(",", ".")
                + ". Pertimbangkan alternatif transportasi yang lebih hemat."
            ),
            "category": "transportasi",
            "saving_estimate": estimasi_hemat(row["total_transportasi"], 0.15),
            "priority": 4
        })

    # Cek pengeluaran hiburan
    if row["rasio_hiburan"] > 0.15 and row["total_hiburan"] >= 300000:
        hasil.append({
            "type": "warning",
            "icon": "🎮",
            "title": "Pengeluaran Hiburan Tinggi",
            "message": (
                f"Pengeluaran hiburan bulan ini sekitar "
                f"Rp{int(row['total_hiburan']):,}".replace(",", ".")
                + ". Pertimbangkan membatasi transaksi hiburan impulsif."
            ),
            "category": "hiburan",
            "saving_estimate": estimasi_hemat(row["total_hiburan"], 0.20),
            "priority": 3
        })

    # Cek pengeluaran belanja
    if row["rasio_belanja"] > 0.18 and row["total_belanja"] >= 300000:
        hasil.append({
            "type": "tip",
            "icon": "🛒",
            "title": "Belanja Bisa Lebih Dikontrol",
            "message": (
                f"Total pengeluaran belanja mencapai "
                f"Rp{int(row['total_belanja']):,}".replace(",", ".")
                + ". Coba buat daftar kebutuhan sebelum berbelanja agar lebih hemat."
            ),
            "category": "belanja",
            "saving_estimate": estimasi_hemat(row["total_belanja"], 0.15),
            "priority": 4
        })

    # Cek pengeluaran akhir pekan
    if (
        row["rasio_akhir_pekan"] > 0.35
        and row["pengeluaran_akhir_pekan"] >= 500000
        and rasio > 0.60
    ):
        hasil.append({
            "type": "tip",
            "icon": "📅",
            "title": "Pengeluaran Akhir Pekan Tinggi",
            "message": (
                f"Sebagian besar pengeluaran terjadi saat akhir pekan "
                f"dengan total sekitar "
                f"Rp{int(row['pengeluaran_akhir_pekan']):,}".replace(",", ".")
                + ". Buat batas pengeluaran khusus weekend agar lebih terkontrol."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(row["pengeluaran_akhir_pekan"], 0.15),
            "priority": 6
        })

    # Tampilkan pesan positif jika keuangan bagus
    if len(hasil) == 0:
        hasil.append({
            "type": "good",
            "icon": "✅",
            "title": "Keuangan Cukup Stabil",
            "message": (
                "Pola keuangan kamu cukup baik. "
                "Pertahankan kebiasaan ini dan mulai sisihkan tabungan rutin."
            ),
            "category": "general",
            "saving_estimate": None,
            "priority": 9
        })

    hasil = sorted(hasil, key=lambda x: x["priority"])[:5]

    for rec in hasil:
        rec.pop("priority", None)

    return add_recommendation_id(hasil)