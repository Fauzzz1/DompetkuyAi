from typing import List, Optional
from pydantic import BaseModel


class Transaction(BaseModel):
    user_id: str
    tanggal: str
    kategori: str
    jumlah: float
    jenis: str
    metode_pembayaran: Optional[str] = None
    profil_user: Optional[str] = "unknown"
    merchant: Optional[str] = "unknown"
    lokasi: Optional[str] = "unknown"


class UserTransactionRequest(BaseModel):
    transactions: List[Transaction]


class ExtractTransactionsRequest(BaseModel):
    text: str


class ExtractedTransaction(BaseModel):
    amount: int
    category: str
    merchant: str
    pay_method: str
    note: str
    type: str
    confidence: float


class ExtractTransactionsResponse(BaseModel):
    timestamp: str
    transaction_count: int
    transactions: List[ExtractedTransaction]


class RecommendationItem(BaseModel):
    type: str
    icon: str
    title: str
    message: str
    category: str
    saving_estimate: Optional[int] = None
    id: str

class PredictionSummary(BaseModel):
    total_pendapatan: int
    total_pengeluaran: int
    selisih: int
    rasio_pengeluaran_pendapatan: float
    jumlah_transaksi: int


class PredictResponse(BaseModel):
    user_id: str
    profil_user: str
    lokasi: str
    financial_status: str
    rule_status: str
    model_status: Optional[str] = None
    recommendation_method: str
    model_confidence: Optional[float] = None
    model_version: str
    timestamp: str
    summary: PredictionSummary
    recommendations: List[RecommendationItem]