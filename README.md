# 💸 DompetKuy AI Service

API berbasis Deep Learning dan Recommendation System untuk analisis kondisi keuangan pengguna berdasarkan histori transaksi.

---

# 🚀 Features

### Financial Status Prediction (`POST /predict`)

Memprediksi kondisi finansial pengguna menjadi:

* good
* tip
* warning
* alert

### NLP Transaction Extraction (`POST /extract-transactions`)

Mengubah transaksi natural language menjadi data transaksi terstruktur.

---

# 🌐 Production URL

```text
https://dompetkuyai-production.up.railway.app
```

---

# 📘 API Documentation

```text
https://dompetkuyai-production.up.railway.app/docs
```

---

# 📌 Model & Endpoints

## 💰 Financial Condition Classification (`POST /predict`)

Memprediksi kondisi keuangan pengguna berdasarkan histori transaksi.

### Jenis Model

Switching Hybrid Recommendation:

* Rule-Based Recommendation
* Hybrid Deep Learning Recommendation

### Model

Deep Neural Network berbasis TensorFlow/Keras.

### Input

Histori transaksi pengguna:

* pendapatan
* pengeluaran
* kategori transaksi
* metode pembayaran
* merchant
* lokasi
* profil pengguna

### Output

Prediksi kondisi finansial:

* good
* tip
* warning
* alert

Serta insight rekomendasi finansial.

---

## 📝 NLP Transaction Extraction (`POST /extract-transactions`)

Mengubah teks transaksi menjadi data transaksi terstruktur.

### Contoh Input

```json
{
  "text": "beli kopi 20 ribu lalu bayar gojek 15 ribu"
}
```

### Output

```json
[
  {
    "category": "makanan",
    "amount": 20000
  },
  {
    "category": "transportasi",
    "amount": 15000
  }
]
```

---

# ⚙️ Installation

```bash
git clone https://github.com/Fauzzz1/DompetkuyAi.git
cd DompetkuyAi
pip install -r requirements.txt
```

---

# ▶️ Run Local

```bash
uvicorn app.main:app --reload
```
