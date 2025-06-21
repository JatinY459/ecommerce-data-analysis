# fixing the path as root directory is 'dashboard'
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# or use this command instead of this code: $env:PYTHONPATH="."; streamlit run dashboard/app.py

import streamlit as st
import pandas as pd

from scripts.data_cleaning import import_data


st.set_page_config(page_title="E-commerce EDA", page_icon="📑", initial_sidebar_state="collapsed")


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

st.subheader("Objective")
st.markdown("""
This dashboard presents a deep-dive exploratory analysis of a large-scale e-commerce dataset.
It helps users explore key trends consumer behavior, delivery performance, product pricing, and payment trends.
The goal is to support better understanding, decision-making, and analysis of the platform's operations.
""")



#col1.metric("Total Revenue (R$)", payments['payment_value'].sum())
#col2.metric("%d%% of Orders with installments", f"{(payments['payment_type'] == 'instalments').mean() * 100:.1f}%")
#col3.metric("", )

st.markdown("""
    ### About the Dataset
            
    The data set used in this Exploratory Data Analysis for E-commerce Platform, is a data set for a Brazilian E-commerce platform which offers their services all over Brazil. This rich dataset captures the *seasonal patterns, cultural events and purchasing behaviour* of Brazil’s population across regions and categories. It provides a detailed look at order patterns, delivery performance, payment methods, product types and regional dynamics.
    The goal is to uncover insights that can improve logistics, marketing, and customer experience for online platforms.
""")

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", orders['order_id'].nunique())
col2.metric("Avg. Delivery Time (hrs)", f"{(orders['delivery_time_gap'].dt.total_seconds().mean() / 3600):.2f}")
col3.metric("Successful Delivery Percentage", f"{(orders['order_status'] == 'delivered').mean() * 100:.1f}%")

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

st.markdown("### 💡 How to Use This Dashboard")

st.markdown("""
This dashboard is designed to help you **explore, analyze, and draw insights** from the e-commerce dataset. Here's what you can do:

- **Track order and delivery trends:** Understand how order volumes, delivery timelines, and regional patterns behave over time.
- **Analyze product and seller dynamics:** Dive into product categories, seller performance, and inventory patterns.
- **Explore payment and shipping insights:** See how customers prefer to pay and how shipping charges vary across orders.
- **Interact with visualizations:** Use filters and controls (where provided) to focus on specific time periods, categories, or regions.
- **Navigate via sidebar:** The sidebar allows you to jump between different sections of the analysis easily.

Use each section to explore specific aspects of the data in depth!
""")


st.markdown("---") 
st.markdown(
    f"**Dashboard Version:** v1.0 | **Last Updated:** {pd.Timestamp.today().strftime('%B %d, %Y')}"
)

st.markdown("""
    <h4 style='text-align: center;'> Created by <span style='font-weight: 800;'>Jatin Yadav</span> </h4>""", unsafe_allow_html=True)

st.markdown("""
            <style>
                .my-btn {
                    background-color: #000;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 10px;
                    border: 2px solid rgb(30,30,30);
                    text-decoration: none;
                    font-size: 1rem;
                    font-weight: bold;
                    transition: 0.3s;
                    margin: 0 1rem;
                }
                .my-btn:hover {
                    background-color: rgb(30,30,30);
                    font-weight: 900;
                    transform: scale(1.02);
                }
             @media (max-width: 600px) {
                .my-btn {
                    display: block;
                    width: 70%;
                    margin: 8px auto;
                }
            }   
            </style>
            <div style='text-align: center; margin-top: 1rem;'>
                <a href='https://github.com/JatinY459/' class='my-btn' target='_blank'>GitHub</a>
                <a href='https://www.linkedin.com/in/jatinyadav459/' class='my-btn' target='_blank'>LinkedIn</a>
                <a href='https://github.com/JatinY459/ecommerce-data-analysis' class='my-btn' target='_blank'>Project Info</a>
            </div>""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
<div style='height: 1.25rem; margin-top: 0.5rem'></div>
📧 Email: 14jatinyadav@gmail.com
<p style='font-style:italic;'>Open for feedback & collaboration! <p>
</div>
""", unsafe_allow_html=True)