import pandas as pd
import numpy as np


def import_data():
    date_cols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_timestamp", "order_estimated_delivery_date"]

    orders = pd.read_csv('../data/processed/orders.csv')
    orders[date_cols] = orders[date_cols].apply(pd.to_datetime, errors='coerce')  # Safely parse all, fallback if weird values

    orders["delivery_time_gap"] = pd.to_timedelta(orders["delivery_time_gap"], errors='coerce')

    order_items = pd.read_csv('../data/processed/order_items.csv')
    customers = pd.read_csv('../data/processed/customers.csv')
    payments = pd.read_csv('../data/processed/payments.csv')
    products = pd.read_csv('../data/processed/products.csv')

    return orders, order_items, customers, payments, products