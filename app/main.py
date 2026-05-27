import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import UserTransactionRequest, ExtractTransactionsRequest
from app.preprocessing import preprocessing
from app.feature_engineering import feature_engineering
from app.rekomendasi import status_rule, rekomendasi_rule
from app.inference import predict_model
from app.monitoring import save_prediction_log
from app.nlp_ekstraksi import multi_transactions
from app.logger import logger


load_dotenv()

ENV = os.getenv("ENV", "development").lower()
IS_PRODUCTION = ENV == "production"

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
MAX_TRANSACTIONS = int(os.getenv("MAX_TRANSACTIONS", "100"))

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
]

status_level = {
    "good": 0,
    "tip": 1,
    "warning": 2,
    "alert": 3,
}


app = FastAPI(
    title="DompetKuy AI API",
    version=MODEL_VERSION,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation error | path={request.url.path} | errors={exc.errors()}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Input tidak valid",
            "errors": exc.errors(),
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception | path={request.url.path} | error={exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_text(text: str) -> str:
    clean_text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        text,
    )
    return clean_text[:MAX_TEXT_LENGTH]

def get_final_status(rule_status: str, model_status: str) -> str:
    rule_score = status_level.get(rule_status)
    model_score = status_level.get(model_status)

    if rule_score is None:
        raise ValueError(f"Rule status tidak valid: {rule_status}")

    if model_score is None:
        raise ValueError(f"Model status tidak valid: {model_status}")

    return rule_status if rule_score >= model_score else model_status

@app.get("/")
def home():
    return {
        "message": "DompetKuy AI API Running",
        "status": "ready",
        "model_version": MODEL_VERSION,
        "environment": ENV,
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_version": MODEL_VERSION,
        "timestamp": now_iso(),
    }

@app.post("/extract-transactions")
def extract_transactions(request: ExtractTransactionsRequest):
    try:
        text = request.text.strip()

        if not text:
            raise ValueError("Teks transaksi tidak boleh kosong")

        if len(text) > MAX_TEXT_LENGTH:
            raise ValueError(
                f"Teks terlalu panjang, maksimal {MAX_TEXT_LENGTH} karakter"
            )

        clean_text = sanitize_text(text)
        results = extract_multiple_transactions(clean_text)

        logger.info(f"Extraction success | count={len(results)}")

        return {
            "timestamp": now_iso(),
            "transaction_count": len(results),
            "transactions": results,
        }

    except ValueError as error:
        logger.warning(f"Extraction validation error | error={error}")
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        logger.error(f"Extraction failed | error={error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Gagal memproses teks transaksi",
        )
        
@app.post("/predict")
def predict(request: UserTransactionRequest):
    try:
        data = [item.model_dump() for item in request.transactions]

        if not data:
            raise ValueError("Transaksi tidak boleh kosong")

        if len(data) > MAX_TRANSACTIONS:
            raise ValueError(
                f"Terlalu banyak transaksi, maksimal {MAX_TRANSACTIONS} per request"
            )

        for item in data:
            if item["jumlah"] <= 0:
                raise ValueError("Jumlah transaksi harus lebih dari 0")

        df_clean = preprocessing(data)

        if df_clean.empty:
            raise ValueError("Data transaksi tidak valid setelah preprocessing")

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
            "timestamp": now_iso(),
            "summary": {
                "total_pendapatan": int(row["total_pendapatan"]),
                "total_pengeluaran": int(row["total_pengeluaran"]),
                "selisih": int(row["selisih"]),
                "rasio_pengeluaran_pendapatan": round(
                    float(row["rasio_pengeluaran_pendapatan"]),
                    3,
                ),
                "jumlah_transaksi": int(row["jumlah_transaksi"]),
            },
            "recommendations": recommendations,
        }

        save_prediction_log(response)

        logger.info(
            f"Prediction success | user_id={row['user_id']} "
            f"| status={final_status} | method={method}"
        )

        return response

    except ValueError as error:
        logger.warning(f"Prediction validation error | error={error}")
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        logger.error(f"Prediction failed | error={error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Gagal memproses prediksi",
        )