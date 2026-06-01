# DompetKuy AI Service

Service AI untuk analisis kondisi keuangan pengguna berdasarkan histori transaksi. Sistem menggunakan kombinasi Deep Learning, Recommendation System, dan NLP untuk menghasilkan insight finansial secara otomatis.

---

## Fitur

### Prediksi Kondisi Finansial

Endpoint:

```text
POST /predict
```

Digunakan untuk memprediksi kondisi finansial pengguna menjadi:

* good
* tip
* warning
* alert

Sistem juga menghasilkan rekomendasi finansial berdasarkan pola transaksi pengguna.

---

### Ekstraksi Transaksi Otomatis

Endpoint:

```text
POST /extract-transactions
```

Mengubah teks transaksi menjadi data transaksi terstruktur secara otomatis.

Contoh:

```text
beli kopi 25rb pakai gopay di Kopi Kenangan
```

akan diproses menjadi:

```json
[
    {
      "amount": 25000,
      "category": "makanan",
      "merchant": "Kopi Kenangan",
      "pay_method": "gopay",
      "note": "beli kopi 25rb pakai gopay di Kopi Kenangan",
      "type": "expense",
      "confidence": 0.95
    }
]
```

---

## Pendekatan Model

Sistem menggunakan pendekatan:

* Rule-Based Recommendation
* Deep Learning Recommendation
* Switching Hybrid Recommendation

Model utama dibangun menggunakan TensorFlow/Keras.

---

## Struktur Project

```bash

DompetkuAi/
├── app/
│   ├── __init__.py
│   ├── feature_engineering.py
│   ├── inference.py
│   ├── load_model.py
│   ├── logger.py
│   ├── main.py
│   ├── monitoring.py
│   ├── nlp_ekstraksi.py
│   ├── preprocessing.py
│   ├── rekomendasi.py
│   ├── schema.py
│   └── utils.py
│
├── models/
│   ├── dompetkuy_model.keras
│   ├── scaler.pkl
│   ├── feature_cols.pkl
│   └── metrics.json
│
├── .dockerignore
├── .gitignore
├── .python-version
├── Dockerfile
├── Procfile
├── README.md
├── requirements.txt
└── runtime.txt
```

## Instalasi

Clone repository:

```bash
git clone https://github.com/Fauzzz1/DompetkuyAi.git
cd DompetkuyAi
```

Install dependency:

```bash
pip install -r requirements.txt
```

---

## Menjalankan API

```bash
uvicorn app.main:app --reload
```

API akan berjalan di:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Production URL

```text
https://dompetkuyai-production.up.railway.app
```

---

## Deployment

Project dideploy menggunakan:

* Railway
* Docker
* FastAPI
* TensorFlow/Keras
