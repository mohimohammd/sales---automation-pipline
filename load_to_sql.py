"""
load_to_sql.py
------------------------
يقرأ آخر ملفات CSV المولّدة اليوم (مبيعات + أسعار صرف) ويدخلها
بشكل تدريجي (incremental load) إلى SQL Server، بدون تكرار البيانات.

الجداول المستهدفة (تُنشأ تلقائياً إن لم تكن موجودة):
- FactSales_Incremental  (الطلبات اليومية الجديدة)
- DimExchangeRate        (أسعار الصرف اليومية)

الاتصال بقاعدة البيانات يُقرأ من متغيرات بيئة (Environment Variables)
حتى لا توضع بيانات الاتصال الحساسة داخل الكود مباشرة.
"""

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

DATA_DIR = Path(__file__).parent.parent / "data" / "incoming"

SQL_SERVER = os.environ["SQL_SERVER_HOST"]        # مثال: myserver.database.windows.net
SQL_DATABASE = os.environ["SQL_DATABASE_NAME"]
SQL_USERNAME = os.environ["SQL_USERNAME"]
SQL_PASSWORD = os.environ["SQL_PASSWORD"]

CONN_STR = (
    f"mssql+pyodbc://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DATABASE}"
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
)

CREATE_SALES_TABLE = """
IF OBJECT_ID('dbo.FactSales_Incremental', 'U') IS NULL
CREATE TABLE dbo.FactSales_Incremental (
    OrderID         VARCHAR(64) PRIMARY KEY,
    OrderDate       DATE NOT NULL,
    CustomerID      INT NOT NULL,
    ProductID       INT NOT NULL,
    CompanyID       INT NOT NULL,
    Category        VARCHAR(50),
    Region          VARCHAR(50),
    Quantity        INT,
    UnitPrice       DECIMAL(12,2),
    GrossAmount     DECIMAL(14,2),
    DiscountPct     DECIMAL(5,2),
    NetAmount       DECIMAL(14,2),
    CurrencyCode    VARCHAR(5),
    LoadedAtUTC     DATETIME2 DEFAULT SYSUTCDATETIME()
);
"""

CREATE_RATES_TABLE = """
IF OBJECT_ID('dbo.DimExchangeRate', 'U') IS NULL
CREATE TABLE dbo.DimExchangeRate (
    RateDate        DATE NOT NULL,
    BaseCurrency    VARCHAR(5) NOT NULL,
    TargetCurrency  VARCHAR(5) NOT NULL,
    Rate            DECIMAL(18,6) NOT NULL,
    LoadedAtUTC     DATETIME2 DEFAULT SYSUTCDATETIME(),
    PRIMARY KEY (RateDate, BaseCurrency, TargetCurrency)
);
"""


def get_today_files():
    today = datetime.utcnow().date().isoformat()
    sales_file = DATA_DIR / f"sales_{today}.csv"
    rates_file = DATA_DIR / f"rates_{today}.csv"
    return sales_file, rates_file


def load_sales(engine, sales_file: Path):
    if not sales_file.exists():
        print(f"[SKIP] لا يوجد ملف مبيعات لليوم: {sales_file}")
        return

    df = pd.read_csv(sales_file)

    with engine.begin() as conn:
        conn.execute(text(CREATE_SALES_TABLE))
        existing_ids = pd.read_sql(
            "SELECT OrderID FROM dbo.FactSales_Incremental", conn
        )["OrderID"].tolist()

    df_new = df[~df["OrderID"].isin(existing_ids)]

    if df_new.empty:
        print("[SKIP] لا توجد طلبات جديدة غير موجودة مسبقاً")
        return

    df_new.to_sql(
        "FactSales_Incremental", engine, if_exists="append",
        index=False, schema="dbo",
    )
    print(f"[OK] تم إدخال {len(df_new)} طلب جديد إلى FactSales_Incremental")


def load_rates(engine, rates_file: Path):
    if not rates_file.exists():
        print(f"[SKIP] لا يوجد ملف أسعار صرف لليوم: {rates_file}")
        return

    df = pd.read_csv(rates_file)

    with engine.begin() as conn:
        conn.execute(text(CREATE_RATES_TABLE))

    # Upsert بسيط: نحذف صفوف اليوم لنفس العملة قبل الإدخال (تفادي تكرار)
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM dbo.DimExchangeRate WHERE RateDate = :d"),
            {"d": df["Date"].iloc[0]},
        )

    df = df.rename(columns={"Date": "RateDate"})
    df.to_sql(
        "DimExchangeRate", engine, if_exists="append",
        index=False, schema="dbo",
    )
    print(f"[OK] تم إدخال {len(df)} سعر صرف إلى DimExchangeRate")


def main():
    engine = create_engine(CONN_STR, fast_executemany=True)
    sales_file, rates_file = get_today_files()

    load_sales(engine, sales_file)
    load_rates(engine, rates_file)


if __name__ == "__main__":
    main()
