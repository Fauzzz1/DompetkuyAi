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


def estimasi_hemat(nilai, persen):
    if not nilai or nilai <= 0:
        return None
    return int(round(nilai * persen, -3))

def add_recommendation_id(recommendations):
    for i, rec in enumerate(recommendations, start=1):
        rec["id"] = f"rec-{i:03d}"

    return recommendations


def rekomendasi_rule(row):
    hasil = []

    if row["rasio_pengeluaran_pendapatan"] > 1:
        hasil.append({
            "type": "alert",
            "icon": "🚨",
            "title": "Pengeluaran Melebihi Pendapatan",
            "message": "Pengeluaran kamu lebih besar dari pendapatan. Prioritaskan kebutuhan utama dulu.",
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(row["total_pengeluaran"], 0.10),
            "priority": 1
        })

    elif row["rasio_pengeluaran_pendapatan"] > 0.85:
        hasil.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Rasio Pengeluaran Tinggi",
            "message": "Pengeluaran sudah cukup dekat dengan pendapatan. Coba kurangi transaksi tidak penting.",
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(row["total_pengeluaran"], 0.08),
            "priority": 2
        })

    if row["rasio_makanan"] > 0.35 and row["total_makanan"] >= 500000:
        hasil.append({
            "type": "warning",
            "icon": "🍽️",
            "title": "Pengeluaran Makanan Tinggi",
            "message": "Porsi pengeluaran makanan cukup besar. Coba buat batas budget makan harian.",
            "category": "makanan",
            "saving_estimate": estimasi_hemat(row["total_makanan"], 0.15),
            "priority": 3
        })

    if row["rasio_hiburan"] > 0.25 and row["total_hiburan"] >= 500000:
        hasil.append({
            "type": "alert",
            "icon": "🎮",
            "title": "Pengeluaran Hiburan Tinggi",
            "message": "Pengeluaran hiburan cukup dominan. Kurangi transaksi hiburan yang impulsif.",
            "category": "hiburan",
            "saving_estimate": estimasi_hemat(row["total_hiburan"], 0.20),
            "priority": 2
        })

    if row["rasio_belanja"] > 0.30 and row["total_belanja"] >= 500000:
        hasil.append({
            "type": "tip",
            "icon": "🛒",
            "title": "Belanja Bisa Lebih Dikontrol",
            "message": "Pengeluaran belanja cukup besar. Buat daftar kebutuhan sebelum belanja.",
            "category": "belanja",
            "saving_estimate": estimasi_hemat(row["total_belanja"], 0.15),
            "priority": 4
        })

    if (row["rasio_akhir_pekan"] > 0.45 and row["pengeluaran_akhir_pekan"] >= 750000 and row["rasio_pengeluaran_pendapatan"] > 0.60 ):
        hasil.append({
            "type": "tip",
            "icon": "📅",
            "title": "Pengeluaran Akhir Pekan Tinggi",
            "message": "Banyak transaksi terjadi saat akhir pekan. Buat anggaran khusus agar pengeluaran lebih terkontrol.",
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(row["pengeluaran_akhir_pekan"],0.15),
            "priority": 7
        })

    if len(hasil) == 0:
        hasil.append({
            "type": "good",
            "icon": "✅",
            "title": "Keuangan Cukup Stabil",
            "message": "Pola keuangan kamu cukup baik. Pertahankan dan mulai sisihkan tabungan rutin.",
            "category": "general",
            "saving_estimate": None,
            "priority": 9
        })

    hasil = sorted(hasil, key=lambda x: x["priority"])[:3]

    for rec in hasil:
        rec.pop("priority", None)

    return add_recommendation_id(hasil)