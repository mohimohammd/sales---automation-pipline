"""
generate_daily_sales.py
------------------------
يولّد دفعة جديدة من طلبات المبيعات لليوم الحالي، بنفس منطق البيانات
الأصلية لمشروع "Enterprise Sales Analytics" (عملاء، منتجات، شركات، مبالغ).

المخرج: ملف CSV باسم sales_YYYY-MM-DD.csv داخل مجلد data/incoming/
يحتوي على دفعة يومية فقط (ليس كل البيانات التاريخية) لمحاكاة "وصول
طلبات جديدة" بشكل واقعي.
"""

import csv
import random
import uuid
from datetime import datetime, date
from pathlib import Path

# ---------- إعدادات قابلة للتعديل ----------
NUM_NEW_ORDERS_PER_DAY = (150, 400)   # نطاق عدد الطلبات الجديدة يومياً
NUM_CUSTOMERS = 48000                  # يطابق حجم بيانات المشروع الحالي
NUM_PRODUCTS = 50000
NUM_COMPANIES = 1000
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "incoming"

PRODUCT_CATEGORIES = [
    "Electronics", "Apparel", "Home & Garden", "Industrial",
    "Food & Beverage", "Healthcare Supplies", "Automotive Parts",
]

REGIONS = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Madinah", "Abha", "Tabuk"]


def generate_orders(order_date: date) -> list[dict]:
    n_orders = random.randint(*NUM_NEW_ORDERS_PER_DAY)
    orders = []
    for _ in range(n_orders):
        order_id = str(uuid.uuid4())
        customer_id = random.randint(1, NUM_CUSTOMERS)
        product_id = random.randint(1, NUM_PRODUCTS)
        company_id = random.randint(1, NUM_COMPANIES)
        quantity = random.randint(1, 25)
        unit_price = round(random.uniform(15, 5000), 2)
        gross_amount = round(quantity * unit_price, 2)
        discount_pct = round(random.choice([0, 0, 0, 5, 10, 15]) / 100, 2)
        net_amount = round(gross_amount * (1 - discount_pct), 2)

        orders.append({
            "OrderID": order_id,
            "OrderDate": order_date.isoformat(),
            "CustomerID": customer_id,
            "ProductID": product_id,
            "CompanyID": company_id,
            "Category": random.choice(PRODUCT_CATEGORIES),
            "Region": random.choice(REGIONS),
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "GrossAmount": gross_amount,
            "DiscountPct": discount_pct,
            "NetAmount": net_amount,
            "CurrencyCode": "SAR",  # يتحول لعملات أخرى لاحقاً عبر أسعار الصرف
        })
    return orders


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.utcnow().date()
    orders = generate_orders(today)

    out_file = OUTPUT_DIR / f"sales_{today.isoformat()}.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)

    print(f"[OK] تم توليد {len(orders)} طلب جديد → {out_file}")


if __name__ == "__main__":
    main()
