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

# Import data
orders, order_items, customers, payments, products = import_data(dashboard=True)

st.title("E-commerce Data Analysis Dashboard")
st.markdown("<p style='font-size:1.5rem; font-weight:700;'>Based on Brazilian E-commerce Platform Insights, Trends, and Behavior Patterns</p>", unsafe_allow_html=True)

st.markdown("""
This dashboard presents a deep-dive exploratory analysis of a large-scale e-commerce dataset.
It uncovers consumer behavior, delivery performance, product pricing, and payment trends.
Use the sidebar to navigate through focused insights from different aspects of the platform's operations.
""")

