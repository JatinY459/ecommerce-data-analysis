import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
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

# delivery time Analysis
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Delivery Time Analysis</h2>""", unsafe_allow_html=True)

x_values = pd.to_numeric(orders["delivery_time_gap_hrs"], errors="coerce").dropna()

fig = px.histogram(x=x_values, nbins=20, opacity=0.6, color_discrete_sequence=["#636EFA"])

hist, bin_edges = np.histogram(x_values, bins=20, density=True)
y_max = hist.max()

# line for on time deliveries, x=0
fig.add_vline(
    x=0,
    line=dict(color="red", width=3, dash="dash"),
    annotation_text="On Time",
    annotation_position="top",
    annotation_font_color="red",
    annotation_font_size=20
)
# adding label for late & early delivery
fig.add_annotation(
    x=x_values.max()* 0.9,
    y=y_max * 500,
    text="Early Deliveries",
    showarrow=False,
    font=dict(color="yellow", size=20),
    yshift=100
)
fig.add_annotation(
    x=x_values.min() * 0.7,
    y=y_max * 500,
    text="Late Deliveries",
    showarrow=False,
    font=dict(color="orange", size=20),
    yshift=100
)
fig.update_layout(
    title="Delivery Time Gap Distribution",
    xaxis_title="Delivery Time Gap (hrs)",
    yaxis_title="Number of Orders",
    template="simple_white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    font=dict(size=14)
)
fig.update_traces(marker_line_width=1, marker_line_color="white") 

st.plotly_chart(fig)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Early Delivered Orders (%)", f"{(x_values > 12).mean() * 100:.1f}%")
col2.metric("Late Delivered Orders (%)", f"{(x_values < -12).mean() * 100:.1f}%")
col3.metric("Delivered on Estimated Day (%)", f"{(x_values.between(-12,12)).mean() * 100:.1f}%")
col4.metric("Average Delivery Time (hrs)", f"{x_values.mean():.2f}")

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Order Status Time Gap Analysis</h2>""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
st.write(orders[orders['order_status'] != 'delivered'])

fig = px.histogram(
    orders,
    x=orders['purchase_to_approval_hours'],
    nbins=100,
    title="Order Approval Time Distribution",
    template="plotly_white",
    marginal="box",
    opacity=0.6
)

# Improve layout
fig.update_layout(
    xaxis_title="Order Purchase to Approval Time (hours)",
    yaxis_title="Count",
    bargap=0.05,
    title_x=0.5
)
fig.update_traces(marker_line_width=1, marker_line_color="white")
col1.plotly_chart(fig)