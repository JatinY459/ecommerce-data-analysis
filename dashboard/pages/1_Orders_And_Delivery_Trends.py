import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from scripts.data_cleaning import import_data

# configuring page
st.set_page_config(page_title="Orders and Delivery Trends - EDA", page_icon="📦", initial_sidebar_state="collapsed", layout='wide')

# importing data
orders, order_items, customers, payments, products = import_data(dashboard=True)

st.title("Orders and Delivery Trends")
st.markdown("""
This page explores key trends in order volumes, statuses, and delivery timelines.  
Understand how the platform performs across order fulfillment stages.  
""")

col1, col2 = st.columns(2)

# Create bar plot
fig = px.bar(
    orders['order_status'].value_counts().reset_index(name='count').rename(columns={'index': 'order_status'}),
    x='order_status',
    y='count',
    color='order_status',
    title='Order Status Distribution',
    text='count',
    labels={'order_status': 'Order Status', 'count': 'Number of Orders'},
)

fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

# Show plot
col1.plotly_chart(fig)

col2.plotly_chart(
    px.bar(
        orders[orders['order_status'] != 'delivered']['order_status'].value_counts().reset_index(name='count').rename(columns={'index': 'order_status'}),
        x='order_status',
        y='count',
        color='order_status',
        title='Order Status Distribution (Excluding Delivered)',
        text='count',
        labels={'order_status': 'Order Status', 'count': 'Number of Orders'},
    ).update_traces(textposition='outside').update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
)

