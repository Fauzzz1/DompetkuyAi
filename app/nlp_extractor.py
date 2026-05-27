import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

valid_categories = [
    "makanan",
    "transport",
    "belanja",
    "hiburan",
    "kesehatan",
    "pendidikan",
    "tagihan",
    "pemasukan",
    "lainnya"
]

valid_pay_methods = [
    "cash",
    "bni",
    "bca",
    "mandiri",
    "bri",
    "bsi",
    "cimb",
    "danamon",
    "permata",
    "gopay",
    "ovo",
    "dana",
    "shopeepay",
    "jenius",
    "cc_visa",
    "cc_mastercard",
    "cc_jcb",
    "cc_amex",
    "lainnya"
]


def normalize_amount(value):
    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).lower().strip()
    text = text.replace("rp", "").strip()

    juta_match = re.search(r"(\d+(?:[,.]\d+)?)\s*(jt|juta)", text)
    if juta_match:
        angka = juta_match.group(1).replace(",", ".")
        return int(float(angka) * 1000000)

    ribu_match = re.search(r"(\d+(?:[,.]\d+)?)\s*(rb|ribu|k)", text)
    if ribu_match:
        angka = ribu_match.group(1).replace(",", ".")
        return int(float(angka) * 1000)

    cleaned = text.replace(".", "").replace(",", "")
    match = re.search(r"\d+", cleaned)

    if not match:
        return 0

    return int(match.group())


def normalize_category(value):
    value = (value or "lainnya").lower().strip()

    category_map = {
        "transportasi": "transport",
        "transport": "transport",
        "makan": "makanan",
        "food": "makanan",
        "entertainment": "hiburan",
        "shopping": "belanja",
        "income": "pemasukan",
        "pendapatan": "pemasukan",
        "gaji": "pemasukan"
    }

    value = category_map.get(value, value)

    if value not in valid_categories:
        return "lainnya"

    return value


def normalize_pay_method(value):
    value = (value or "lainnya").lower().strip()
    value = value.replace(" ", "_").replace("-", "_")

    method_map = {
        "tunai": "cash",
        "mastercard": "cc_mastercard",
        "visa": "cc_visa",
        "jcb": "cc_jcb",
        "amex": "cc_amex",
        "qris": "lainnya",
        "debit": "lainnya"
    }

    value = method_map.get(value, value)

    if value not in valid_pay_methods:
        return "lainnya"

    return value


def normalize_type(value, category):
    value = (value or "").lower().strip()

    if value in ["expense", "income"]:
        return value

    if category == "pemasukan":
        return "income"

    return "expense"


def fallback_extract(text):
    lower_text = text.lower()
    amount = normalize_amount(text)

    category = "lainnya"

    if any(word in lower_text for word in ["kopi", "makan", "ayam", "nasi", "resto", "cafe"]):
        category = "makanan"
    elif any(word in lower_text for word in ["gojek", "grab", "ojek", "transport", "bensin"]):
        category = "transport"
    elif any(word in lower_text for word in ["shopee", "tokopedia", "belanja"]):
        category = "belanja"
    elif any(word in lower_text for word in ["game", "bioskop", "netflix", "spotify"]):
        category = "hiburan"
    elif any(word in lower_text for word in ["gaji", "freelance", "bayaran"]):
        category = "pemasukan"

    pay_method = "lainnya"

    for method in valid_pay_methods:
        if method in lower_text:
            pay_method = method
            break

    transaction_type = normalize_type(None, category)

    return {
        "amount": amount,
        "category": category,
        "merchant": "unknown",
        "pay_method": pay_method,
        "note": text,
        "type": transaction_type,
        "confidence": 0.5
    }
    
def extract_multiple_transactions(text):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return [fallback_extract(text)]

    client = genai.Client(api_key=api_key)

    prompt = f"""
Ekstrak semua transaksi dari teks berikut menjadi JSON array.

Teks:
{text}

Aturan:
- Balas JSON array saja tanpa markdown.
- Setiap item wajib punya amount, category, merchant, pay_method, type, confidence.
- amount harus integer rupiah.
- category harus salah satu: makanan, transport, belanja, hiburan, kesehatan, pendidikan, tagihan, pemasukan, lainnya.
- pay_method harus salah satu: cash, bni, bca, mandiri, bri, bsi, cimb, danamon, permata, gopay, ovo, dana, shopeepay, jenius, cc_visa, cc_mastercard, cc_jcb, cc_amex, lainnya.
- type harus expense atau income.
"""

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            break
        except Exception:
            if attempt == 2:
                return [fallback_extract(text)]
            time.sleep(1.5)

    try:
        raw_text = response.text.strip()
        raw_text = raw_text.replace("```json", "")
        raw_text = raw_text.replace("```", "").strip()

        result = json.loads(raw_text)

        if isinstance(result, dict):
            result = [result]

        if not isinstance(result, list):
            return [fallback_extract(text)]

    except Exception:
        return [fallback_extract(text)]

    transactions = []

    for item in result:
        if not isinstance(item, dict):
            continue

        category = normalize_category(item.get("category"))

        confidence = item.get("confidence", 0.8)

        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.8

        confidence = max(0.0, min(confidence, 0.95))

        transactions.append({
            "amount": normalize_amount(item.get("amount")),
            "category": category,
            "merchant": item.get("merchant") or "unknown",
            "pay_method": normalize_pay_method(item.get("pay_method")),
            "note": text,
            "type": normalize_type(item.get("type"), category),
            "confidence": confidence
        })

    if not transactions:
        return [fallback_extract(text)]

    return transactions