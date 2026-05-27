import pandas as pd


def preprocessing(data):
    df = pd.DataFrame(data)

    df.columns = df.columns.str.lower().str.strip()

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce")

    for col in ["user_id", "kategori", "jenis", "profil_user", "merchant", "lokasi"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["kategori"] = df["kategori"].str.lower()
    df["jenis"] = df["jenis"].str.lower()

    df = df.dropna(subset=["user_id", "tanggal", "jumlah", "kategori", "jenis"])
    df = df[df["jumlah"] > 0]

    if df.empty:
        raise ValueError("Data transaksi kosong atau tidak valid.")

    df["hari_dalam_minggu"] = df["tanggal"].dt.dayofweek
    df["akhir_pekan"] = df["hari_dalam_minggu"].isin([5, 6]).astype(int)

    return df