from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")

customers = pd.read_csv(PROCESSED_DIR / "customers.csv")
orders = pd.read_csv(PROCESSED_DIR / "orders.csv")
order_items = pd.read_csv(PROCESSED_DIR / "order_items.csv")
products = pd.read_csv(PROCESSED_DIR / "products.csv")
geo = pd.read_csv(PROCESSED_DIR / "geolocation_lookup.csv")

print("=" * 80)
print("PROCESSED DATA VALIDATION")

# 1. Check row counts
print("\n1. Row counts")
print(f"Customers: {len(customers):,}")
print(f"Orders: {len(orders):,}")
print(f"Order items: {len(order_items):,}")
print(f"Products: {len(products):,}")
print(f"Geolocation lookup: {len(geo):,}")

# 2. Geolocation must have one row per ZIP
print("\n2. Geolocation lookup")
print(
    f"Duplicate ZIP prefixes: "
    f"{geo['geolocation_zip_code_prefix'].duplicated().sum():,}"
)

# 3. Product categories should have English labels
print("\n3. Product categories")
print(
    f"Missing English category names: "
    f"{products['product_category_name_english'].isna().sum():,}"
)

print(
    f"'unknown' categories: "
    f"{(products['product_category_name_english'] == 'unknown').sum():,}"
)

# 4. Delivery metrics
print("\n4. Delivery metrics")

delivered = orders[orders["order_status"] == "delivered"].copy()

print(f"Delivered orders: {len(delivered):,}")
print(
    f"Delivered orders missing delivery_days: "
    f"{delivered['delivery_days'].isna().sum():,}"
)

print(
    f"Negative delivery_days: "
    f"{(orders['delivery_days'] < 0).sum():,}"
)

print(
    f"Late deliveries: "
    f"{orders['is_late_delivery'].sum():,}"
)

# 5. Referential integrity
print("\n5. Referential integrity")

orphan_items = ~order_items["order_id"].isin(orders["order_id"])

print(
    f"Order items without matching order: "
    f"{orphan_items.sum():,}"
)

# 6. Payments, reviews, and sellers
print("\n6. Payments, reviews, and sellers")

payments = pd.read_csv(PROCESSED_DIR / "payments.csv")
reviews = pd.read_csv(PROCESSED_DIR / "reviews.csv")
sellers = pd.read_csv(PROCESSED_DIR / "sellers.csv")

orphan_payments = ~payments["order_id"].isin(orders["order_id"])
orphan_reviews = ~reviews["order_id"].isin(orders["order_id"])
orphan_sellers = ~order_items["seller_id"].isin(sellers["seller_id"])

print(
    f"Payments without matching order: "
    f"{orphan_payments.sum():,}"
)

print(
    f"Reviews without matching order: "
    f"{orphan_reviews.sum():,}"
)

print(
    f"Order items without matching seller: "
    f"{orphan_sellers.sum():,}"
)

print(
    f"Missing payment values: "
    f"{payments['payment_value'].isna().sum():,}"
)

print(
    f"Missing review scores: "
    f"{reviews['review_score'].isna().sum():,}"
)

print("\nValidation completed.")