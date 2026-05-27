from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    UserTransactionRequest,
    ExtractTransactionsRequest
)
from app.preprocessing import preprocessing
from app.feature_engineering import feature_engineering
from app.recommendation_engine import status_rule, rekomendasi_rule
from app.inference import predict_model
from app.monitoring import save_prediction_log
from app.nlp_extractor import extract_multiple_transactions
from app.logger import logger

app = FastAPI(
    title="DompetKuy AI API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_VERSION = "v1.0"

status_level = {
    "good": 0,
    "tip": 1,
    "warning": 2,
    "alert": 3
}


def get_final_status(rule_status, model_status):
    if status_level[rule_status] >= status_level[model_status]:
        return rule_status

    return model_status


@app.get("/")
def home():
    return {
        "message": "DompetKuy AI API Running",
        "status": "ready",
        "model_version": MODEL_VERSION
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_version": MODEL_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/extract-transactions")
def extract_transactions(request: ExtractTransactionsRequest):
    try:
        text = request.text.strip()

        if not text:
            raise ValueError("Teks transaksi tidak boleh kosong")

        results = extract_multiple_transactions(text)

        logger.info(
            f"Multiple transaction extraction success | "
            f"count={len(results)}"
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_count": len(results),
            "transactions": results
        }

    except Exception as error:
        logger.error(f"Multiple transaction extraction failed: {str(error)}")

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post("/predict")
def predict(request: UserTransactionRequest):
    try:
        data = [item.model_dump() for item in request.transactions]

        if not data:
            raise ValueError("Transaksi tidak boleh kosong")

        for item in data:
            if item["jumlah"] <= 0:
                raise ValueError("Jumlah transaksi harus lebih dari 0")

        df_clean = preprocessing(data)

        if df_clean.empty:
            raise ValueError("Data transaksi tidak valid")

        features = feature_engineering(df_clean)
        row = features.iloc[0]

        rule_status = status_rule(row)
        recommendations = rekomendasi_rule(row)

        model_status = None
        confidence = None

        if row["jumlah_transaksi"] < 20:
            final_status = rule_status
            method = "rule_based"
        else:
            model_status, confidence = predict_model(features)
            final_status = get_final_status(rule_status, model_status)
            method = "hybrid"

        response = {
            "user_id": row["user_id"],
            "profil_user": row["profil_user"],
            "lokasi": row["lokasi"],
            "financial_status": final_status,
            "rule_status": rule_status,
            "model_status": model_status,
            "recommendation_method": method,
            "model_confidence": confidence,
            "model_version": MODEL_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_pendapatan": int(row["total_pendapatan"]),
                "total_pengeluaran": int(row["total_pengeluaran"]),
                "selisih": int(row["selisih"]),
                "rasio_pengeluaran_pendapatan": round(
                    float(row["rasio_pengeluaran_pendapatan"]),
                    3
                ),
                "jumlah_transaksi": int(row["jumlah_transaksi"])
            },
            "recommendations": recommendations
        }

        save_prediction_log(response)

        logger.info(
            f"Prediction success | "
            f"user_id={row['user_id']} | "
            f"status={final_status} | "
            f"method={method}"
        )

        return response

    except Exception as error:
        logger.error(f"Prediction failed: {str(error)}")

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )