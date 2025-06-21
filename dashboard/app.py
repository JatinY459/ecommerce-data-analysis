# fixing the path as root directory is 'dashboard'
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# or use this command instead of this code: $env:PYTHONPATH="."; streamlit run dashboard/app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scripts.data_cleaning import import_data

# styles
st.markdown(
    """
    <style>
    div[data-testid="stExpander"] summary p {
        font-size: 1.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Import data
orders, order_items, customers, payments, products = import_data(dashboard=True)

st.title("E-commerce Data Analysis Dashboard")
st.markdown("<p style='font-size:1.5rem; font-weight:700;'>A data-driven exploration of orders, products, payments, and logistics patterns</p>", unsafe_allow_html=True)

st.markdown("""
This dashboard presents a deep-dive exploratory analysis of a large-scale e-commerce dataset.
It uncovers consumer behavior, delivery performance, product pricing, and payment trends.
""")

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", orders['order_id'].nunique())
col2.metric("Avg. Delivery Time (hrs)", f"{(orders['delivery_time_gap'].dt.total_seconds().mean() / 3600):.2f}")
col3.metric("Successful Delivery Percentage", f"{(orders['order_status'] == 'delivered').mean() * 100:.1f}%")

#col1.metric("Total Revenue (R$)", payments['payment_value'].sum())
#col2.metric("%d%% of Orders with installments", f"{(payments['payment_type'] == 'instalments').mean() * 100:.1f}%")
#col3.metric("", )

st.markdown("""
    ### About the Dataset
            
    The data set used in this Exploratory Data Analysis for E-commerce Platform, is a data set for a Brazilian E-commerce platform which offers their services all over Brazil. This rich dataset captures the *seasonal patterns, cultural events and purchasing behaviour* of Brazil’s population across regions and categories. It provides a detailed look at order patterns, delivery performance, payment methods, product types and regional dynamics.
    The goal is to uncover insights that can improve logistics, marketing, and customer experience for online platforms.
""")

# Dataset Info (optional)
with st.expander("📂 Dataset Information"):
    st.markdown("""
    The **Ecommerce Order & Supply Chain Dataset** represents transactional data from an e-commerce platform operating in Brazil, covering **84,402 orders** placed between **2017 and 2018**. It includes detailed information on orders, products, customers, sellers, payments, shipping, and delivery timelines — offering a comprehensive view into the dynamics of Brazil’s online retail and logistics ecosystem. The data enables analysis of fulfillment performance, payment preferences, product trends, and much more.
    
    The data is divided into several files, each focusing on a different aspect of the e-commerce workflow:
    
    - **orders.csv**: Details of each order including status, timestamps (purchase, approval, delivery).
    - **customers.csv**: Customer location data (state, city, zip code prefix).
    - **products.csv**: Product details like category, weight, and dimensions.
    - **order_items.csv**: Order-item data linking orders to products and sellers, with price and shipping charges.
    - **payments.csv**: Payment type, value, installments, and differences from order totals.


    You can [view the dataset on Kaggle](https://www.kaggle.com/datasets/bytadit/ecommerce-order-dataset).

    """)
