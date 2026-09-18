"""
fetch_exchange_rates.py
------------------------
يجلب أسعار الصرف الحقيقية اليومية (أساس SAR) من exchangerate-api.com
(نسخة مجانية، بدون مفتاح API للاستخدام الأساسي عبر open access endpoint).

المخرج: ملف CSV باسم rates_YYYY-MM-DD.csv داخل data/incoming/
"""

import csv
import os
from datetime import datetime
from pathlib import Path

import requests

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "incoming"

# لو حصلت على API key مجاني من exchangerate-api.com ضعه كمتغير بيئة
# لدقة وموثوقية أعلى. بدون مفتاح، نستخدم endpoint المفتوح (limited).
API_KEY = os.environ.get("EXCHANGE_RATE_API_KEY", "")

TARGET_CURRENCIES = ["USD", "EUR", "GBP", "AED", "EGP", "INR"]


def fetch_rates(base: str = "SAR") -> dict:
    if API_KEY:
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"
    else:
        # endpoint مفتوح بديل بدون مفتاح (exchangerate.host)
        url = f"https://api.exchangerate.host/latest?base={base}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()

    rates = data.get("conversion_rates") or data.get("rates")
    if not rates:
        raise ValueError("لم يتم العثور على أسعار صرف في استجابة الـ API")
    return rates


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.utcnow().date()

    rates = fetch_rates(base="SAR")

    rows = []
    for currency in TARGET_CURRENCIES:
        if currency in rates:
            rows.append({
                "Date": today.isoformat(),
                "BaseCurrency": "SAR",
                "TargetCurrency": currency,
                "Rate": rates[currency],
            })

    out_file = OUTPUT_DIR / f"rates_{today.isoformat()}.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "BaseCurrency", "TargetCurrency", "Rate"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] تم جلب {len(rows)} سعر صرف → {out_file}")


if __name__ == "__main__":
    main()
