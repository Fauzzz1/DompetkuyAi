#Rule menentukan hasil rekomendasi berdasarkan pola pengeluaran
def status_rule(row):
    rasio = row["rasio_pengeluaran_pendapatan"]
    if row["total_pendapatan"] == 0 and row["total_pengeluaran"] > 0:
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

def format_rupiah(nilai):
    return f"Rp{abs(int(nilai)):,}".replace(",", ".")

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
    if total_pendapatan == 0 and total_pengeluaran > 0:
        hasil.append ({
            "type": "alert",
            "icon": "🚨",
            "title": "Pengeluaran Melebihi Pendapatan",
            "message": (
                f"Kamu memiliki pengeluaran sebesar "
                f"{format_rupiah(total_pengeluaran)} "
                f"tapi belum ada pendapatan yang tercatat. "
                f"Tambahkan data pendapatan agar analisis lebih akurat."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(total_pengeluaran, 0.10),
            "priority": 1
        })
        
    elif rasio > 1:
        hasil.append({
            "type": "alert",
            "icon": "🚨",
            "title": "Pengeluaran Melebihi Pendapatan",
            "message": (
                f"Total pengeluaran kamu sudah mencapai "
                f"{rasio * 100:.1f}% dari pendapatan bulanan. "
                f"Kurangi pengeluaran tidak perlu dan prioritaskan kebutuhan utama."
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
                f"Kamu memakai sekitar "
                f"{rasio * 100:.1f}% dari total pendapatan bulan ini. "
                f"Coba tekan pengeluaran agar masih ada ruang untuk menabung."
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
                f"Rasio pengeluaran kamu saat ini sekitar "
                f"{rasio * 100:.1f}% dari pendapatan. "
                f"Masih cukup aman, tapi sebaiknya mulai dikontrol."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(total_pengeluaran, 0.05),
            "priority": 5
        })

    elif total_pendapatan > 0:
        hasil.append({
            "type": "good",
            "icon": "✅",
            "title": "Rasio Keuangan Sehat",
            "message": (
                f"Rasio pengeluaran kamu bulan ini sekitar "
                f"{rasio * 100:.1f}%. "
                f"Kamu menghabiskan lebih sedikit dari pendapatan. Pertahankan."
            ),
            "category": "general",
            "saving_estimate": None,
            "priority": 8
        })
    if total_pendapatan > 0:
        target_tabungan = total_pendapatan * 0.20

        if selisih < 0:
            hasil.append({
                "type": "alert",
                "icon": "📉",
                "title": "Keuangan Mengalami Defisit",
                "message": (
                    f"Bulan ini kamu mengalami defisit sekitar "
                    f"{format_rupiah(selisih)}. "
                    f"Pengeluaran sudah melebihi pendapatan,kamu perlu menghemat dan kurangi pengeluaran tidak perlu."
                ),
                "category": "tabungan",
                "saving_estimate": estimasi_hemat(total_pengeluaran, 0.10),
                "priority": 2
            })
        elif selisih < total_pendapatan * 0.10:
            hasil.append({
                "type": "warning",
                "icon": "💰",
                "title": "Sisa Saldo Bulanan Terlalu Kecil",
                "message": (
                    f"Sisa saldo bulan ini hanya sekitar "
                    f"{format_rupiah(selisih)}. "
                    f"Usahakan sisakan minimal 10% dari pendapatan untuk dana darurat."
                ),
                "category": "tabungan",
                "saving_estimate": estimasi_hemat(total_pendapatan, 0.10),
                "priority": 2
            })
        elif selisih < target_tabungan:
            hasil.append({
                "type": "tip",
                "icon": "💡",
                "title": "Alokasi Tabungan Bisa Ditingkatkan",
                "message": (
                    f"Dengan pendapatan {format_rupiah(total_pendapatan)}, "
                    f"idealnya kamu menabung sekitar {format_rupiah(target_tabungan)} "
                    f"atau 20% dari pendapatan."
                ),
                "category": "tabungan",
                "saving_estimate": estimasi_hemat(target_tabungan - selisih, 1),
                "priority": 5
            })

    if row["rasio_makanan"] > 0.20 and row["total_makanan"] >= 300000:
        hasil.append({
            "type": "warning",
            "icon": "🍽️",
            "title": "Pengeluaran Makanan Cukup Tinggi",
            "message": (
                f"Pengeluaran makanan mencapai "
                f"{format_rupiah(row['total_makanan'])} "
                f"atau sekitar {row['rasio_makanan'] * 100:.1f}% dari total pengeluaran. "
                f"Coba buat batas budget makan harian."
            ),
            "category": "makanan",
            "saving_estimate": estimasi_hemat(row["total_makanan"], 0.15),
            "priority": 3
        })

    if row["rasio_transportasi"] > 0.15 and row["total_transportasi"] >= 300000:
        hasil.append({
            "type": "tip",
            "icon": "🚗",
            "title": "Biaya Transportasi Cukup Tinggi",
            "message": (
                f"Biaya transportasi bulan ini sekitar "
                f"{format_rupiah(row['total_transportasi'])}. "
                f"Pertimbangkan rute yang lebih hemat atau kurangi perjalanan tidak penting."
            ),
            "category": "transportasi",
            "saving_estimate": estimasi_hemat(row["total_transportasi"], 0.15),
            "priority": 4
        })

    if row["rasio_belanja"] > 0.18 and row["total_belanja"] >= 300000:
        hasil.append({
            "type": "tip",
            "icon": "🛒",
            "title": "Belanja Bisa Lebih Dikontrol",
            "message": (
                f"Total pengeluaran belanja mencapai "
                f"{format_rupiah(row['total_belanja'])}. "
                f"Buat daftar kebutuhan sebelum belanja agar tidak impulsif."
            ),
            "category": "belanja",
            "saving_estimate": estimasi_hemat(row["total_belanja"], 0.15),
            "priority": 4
        })

    if row["rasio_hiburan"] > 0.15 and row["total_hiburan"] >= 300000:
        hasil.append({
            "type": "warning",
            "icon": "🎮",
            "title": "Pengeluaran Hiburan Tinggi",
            "message": (
                f"Pengeluaran hiburan bulan ini sekitar "
                f"{format_rupiah(row['total_hiburan'])}. "
                f"Kurangi transaksi hiburan impulsif agar cashflow lebih aman."
            ),
            "category": "hiburan",
            "saving_estimate": estimasi_hemat(row["total_hiburan"], 0.20),
            "priority": 3
        })

    elif row["total_hiburan"] >= 100000:
        hasil.append({
            "type": "tip",
            "icon": "🔔",
            "title": "Langganan atau Hiburan Terdeteksi",
            "message": (
                f"Ada pengeluaran hiburan sekitar "
                f"{format_rupiah(row['total_hiburan'])}. "
                f"Coba cek langganan seperti streaming, musik, atau layanan digital yang jarang dipakai."
            ),
            "category": "hiburan",
            "saving_estimate": estimasi_hemat(row["total_hiburan"], 0.30),
            "priority": 6
        })

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
                f"Pengeluaran akhir pekan mencapai "
                f"{format_rupiah(row['pengeluaran_akhir_pekan'])}. "
                f"Buat batas khusus untuk weekend agar tidak melebihi anggaran."
            ),
            "category": "lainnya",
            "saving_estimate": estimasi_hemat(row["pengeluaran_akhir_pekan"], 0.15),
            "priority": 6
        })

    if len(hasil) == 0:
        hasil.append({
            "type": "good",
            "icon": "✅",
            "title": "Keuangan Cukup Stabil",
            "message": "Pola keuangan kamu cukup baik dan masih terkontrol.",
            "category": "general",
            "saving_estimate": None,
            "priority": 9
        })
    hasil = sorted(hasil, key=lambda x: x["priority"])[:5]
    for rec in hasil:
        rec.pop("priority", None)
    return add_recommendation_id(hasil)