from pathlib import Path
import sqlite3
import pandas as pd


PROCESSED_DIR = Path("data/processed")
DATABASE_PATH = Path("data/ecommerce.db")


tables = {
    "customers": "customers.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
    "products": "products.csv",
    "geolocation": "geolocation_lookup.csv",
    "payments": "payments.csv",
    "reviews": "reviews.csv",
    "sellers": "sellers.csv",
}


connection = sqlite3.connect(DATABASE_PATH)


for table_name, file_name in tables.items():
    df = pd.read_csv(PROCESSED_DIR / file_name)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )

    print(
        f"Created {table_name}: "
        f"{len(df):,} rows"
    )


connection.close()

print(f"\nDatabase created: {DATABASE_PATH}")
