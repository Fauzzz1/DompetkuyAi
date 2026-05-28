import pandas as pd

# Validasi kolom wajib, normalisasi tipe data, dan ekstraksi fitur waktu
def preprocessing(data):
    required_cols = ["user_id", "tanggal", "jumlah", "kategori", "jenis"]

    df = pd.DataFrame(data)
    df.columns = df.columns.str.lower().str.strip()

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan: {missing}")

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce")

    for col in ["user_id", "kategori", "jenis", "profil_user", "merchant", "lokasi"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["kategori"] = df["kategori"].str.lower()
    df["jenis"] = df["jenis"].str.lower()

    jenis_map = {
        "income": "pendapatan",
        "expense": "pengeluaran"
    }
    df["jenis"] = df["jenis"].map(jenis_map).fillna(df["jenis"])
    df = df.dropna(subset=required_cols)
    df = df[df["jumlah"] > 0]

    if df.empty:
        raise ValueError("Data transaksi tidak valid.")
        
    df["hari_dalam_minggu"] = df["tanggal"].dt.dayofweek
    df["akhir_pekan"] = df["hari_dalam_minggu"].isin([5, 6]).astype(int)
    return df