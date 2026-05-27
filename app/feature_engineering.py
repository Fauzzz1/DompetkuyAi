import pandas as pd
from app.utils import aman_bagi


def feature_engineering(df):
    user_id = df["user_id"].iloc[0]

    df_income = df[df["jenis"] == "pendapatan"].copy()
    df_expense = df[df["jenis"] == "pengeluaran"].copy()

    total_pendapatan = df_income["jumlah"].sum()
    total_pengeluaran = df_expense["jumlah"].sum()

    hasil = {
        "user_id": user_id,
        "profil_user": df["profil_user"].mode()[0] if "profil_user" in df.columns else "unknown",
        "lokasi": df["lokasi"].mode()[0] if "lokasi" in df.columns else "unknown",
        "jumlah_transaksi": len(df),
        "total_pendapatan": total_pendapatan,
        "total_pengeluaran": total_pengeluaran,
        "selisih": total_pendapatan - total_pengeluaran,
        "rata_rata_transaksi": df["jumlah"].mean(),
        "transaksi_terbesar": df["jumlah"].max(),
        "transaksi_terkecil": df["jumlah"].min(),
        "jumlah_transaksi_pendapatan": len(df_income),
        "jumlah_transaksi_pengeluaran": len(df_expense),
        "rata_rata_pengeluaran": df_expense["jumlah"].mean() if len(df_expense) > 0 else 0,
    }

    hasil["rasio_pengeluaran_pendapatan"] = aman_bagi(
        total_pengeluaran,
        total_pendapatan
    )

    lama_hari = (df["tanggal"].max() - df["tanggal"].min()).days + 1
    hasil["avg_daily_spending"] = aman_bagi(total_pengeluaran, lama_hari)

    kategori_utama = ["makanan", "transportasi", "belanja", "hiburan", "tagihan"]

    for kategori in kategori_utama:
        total_kategori = df_expense[df_expense["kategori"] == kategori]["jumlah"].sum()

        hasil[f"total_{kategori}"] = total_kategori
        hasil[f"rasio_{kategori}"] = aman_bagi(total_kategori, total_pengeluaran)

    weekend_expense = df_expense[df_expense["akhir_pekan"] == 1]["jumlah"].sum()
    hasil["pengeluaran_akhir_pekan"] = weekend_expense
    hasil["rasio_akhir_pekan"] = aman_bagi(weekend_expense, total_pengeluaran)

    return pd.DataFrame([hasil])