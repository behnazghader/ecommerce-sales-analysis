from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Load data
# --------------------------------------------------

customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
order_items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
translation = pd.read_csv(
    RAW_DIR / "product_category_name_translation.csv"
)
geolocation = pd.read_csv(
    RAW_DIR / "olist_geolocation_dataset.csv"
)


# --------------------------------------------------
# 1. Convert text columns to real dates
# --------------------------------------------------

order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in order_date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce",
    )

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce",
)


# --------------------------------------------------
# 2. Create delivery-related metrics
# --------------------------------------------------

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

orders["is_late_delivery"] = (
    orders["order_delivered_customer_date"]
    > orders["order_estimated_delivery_date"]
)


# --------------------------------------------------
# 3. Add English product category names
# --------------------------------------------------

products = products.merge(
    translation,
    on="product_category_name",
    how="left",
)

manual_translations = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos":
        "portable_kitchen_and_food_preparation_appliances",
}

products["product_category_name_english"] = (
    products["product_category_name_english"]
    .fillna(products["product_category_name"].map(manual_translations))
    .fillna("unknown")
)


# --------------------------------------------------
# 4. Create one geolocation row per ZIP prefix
# --------------------------------------------------

geolocation = geolocation.drop_duplicates()

geo_lookup = (
    geolocation
    .groupby("geolocation_zip_code_prefix", as_index=False)
    .agg(
        geolocation_lat=("geolocation_lat", "median"),
        geolocation_lng=("geolocation_lng", "median"),
    )
)


# --------------------------------------------------
# 5. Save processed tables
# --------------------------------------------------

customers.to_csv(
    PROCESSED_DIR / "customers.csv",
    index=False,
)

orders.to_csv(
    PROCESSED_DIR / "orders.csv",
    index=False,
)

order_items.to_csv(
    PROCESSED_DIR / "order_items.csv",
    index=False,
)

products.to_csv(
    PROCESSED_DIR / "products.csv",
    index=False,
)

geo_lookup.to_csv(
    PROCESSED_DIR / "geolocation_lookup.csv",
    index=False,
)


print("Processed datasets created successfully.")
print(f"Customers: {len(customers):,}")
print(f"Orders: {len(orders):,}")
print(f"Order items: {len(order_items):,}")
print(f"Products: {len(products):,}")
print(f"Geolocation lookup: {len(geo_lookup):,}")