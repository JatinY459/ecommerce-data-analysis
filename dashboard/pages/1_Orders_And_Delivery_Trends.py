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

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Bar Plot for Order Statuses for all Orders</h2>""", unsafe_allow_html=True)
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

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Monthly Order Volume Trends</h2>""", unsafe_allow_html=True)

monthly_counts = orders.groupby(orders['order_purchase_timestamp'].dt.to_period('M')).size().reset_index()
monthly_counts.columns = ['month', 'order_count']
monthly_counts['month'] = monthly_counts['month'].dt.strftime('%m-%Y')
fig = px.line(
    monthly_counts,
    x='month',
    y='order_count',
    title='Monthly Order Volume Trends',
    labels={'month': 'Month', 'order_count': 'Number of Orders'},
).update_traces(mode='lines+markers')

fig.update_layout(
    xaxis=dict(tickmode='array', tickvals=monthly_counts['month'], ticktext=monthly_counts['month']),
    yaxis=dict(tickformat=',d')
)
st.plotly_chart(fig)