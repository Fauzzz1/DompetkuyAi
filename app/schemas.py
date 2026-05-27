from pydantic import BaseModel
from typing import List, Optional


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