import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scripts.utils import expander_styles, get_state_code_names
from scripts.data_cleaning import import_data

# configuring page
st.set_page_config(page_title="Customer Geography & Behavior - EDA", page_icon="👤", initial_sidebar_state="expanded", layout='wide')
# importing data
orders, order_items, customers, payments, products = import_data(dashboard=True)
state_names_dict = get_state_code_names()
# filter
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year:", options=[2017, 2018, 'All'], index=2)
selected_order_status = st.sidebar.multiselect(
    "Select Order Status:",
    options=["delivered", "shipped", "canceled", "approved", "processing", "invoiced"],
    default=["delivered", "shipped", "canceled", "approved", "processing", "invoiced"]
)

# TODO: see if these filters are needed or not
filtered_orders = orders[orders["order_purchase_timestamp"].dt.year == int(selected_year)] if selected_year != 'All' else orders
filtered_orders = filtered_orders[filtered_orders["order_status"].isin(selected_order_status)]

# TODO: see if i can filter customers based on filtered orders
filtered_customers = customers[customers["customer_id"].isin(filtered_orders["customer_id"])]
customers_by_state = filtered_customers.groupby('customer_state')['customer_id'].nunique().reset_index()
customers_by_state = customers_by_state.rename(columns={'customer_id': 'orders_count'})

st.title("Customer Geography and Behavior Analysis")
st.markdown("""
This page explores where customers come from, their order patterns, and regional influences on logistics and engagement.  
Gain insights into key markets and delivery challenges.  
<p style='font-style:italic; margin-top:-8px;'>*Use side bar for filters</p>
""", unsafe_allow_html=True)
st.markdown("**customer_id* is not a unique identifier for customers, hence customer lack unique id in this dataset.")

col1, col2, col3 = st.columns(3)
col1.metric("Total Unique Customers Ids", f"{filtered_customers.shape[0]:,}")
col2.metric("Cities Reached", f"{(filtered_customers['customer_city'].nunique())}")
col3.metric("Top State", f"{customers_by_state.loc[customers_by_state['orders_count'].idxmax(), 'customer_state']} ({state_names_dict[customers_by_state.loc[customers_by_state['orders_count'].idxmax(), 'customer_state']]})")


st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Bar Plot for Order Statuses for all Orders</h2>""", unsafe_allow_html=True)
st.markdown("<p style='font-style:italic;'>Click on legend items to filter specific order statuses for better visibility.</p>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
fig = px.bar(
    filtered_orders['order_status'].value_counts().reset_index(name='count').rename(columns={'index': 'order_status'}),
    x="order_status",
    y="count",
    color="order_status",
    title="Order Status Distribution (Log Scale (base 10))",
    text='count',
    labels={'order_status': 'Order Status', 'count': 'Number of Orders'},
)

fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
fig.update_yaxes(dtick=1, title="Number of Orders (log base 10)", type='log', tickformat=',d')
col1.plotly_chart(fig)

# pie chart for Order Status Distribution
fig = px.pie(
    filtered_orders['order_status'].value_counts().reset_index(name='count').rename(columns={'index': 'order_status'}),
    names='order_status',
    values='count',
    title='Order Status Distribution',
    labels={'order_status': 'Order Status', 'count': 'Number of Orders'},
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}")
col2.plotly_chart(fig)

with st.expander("Order Status Distribution Summary"):
    st.markdown("- Delivered orders dominate, showing a great order fulfillment performance.")
    st.markdown("- Shipped and canceled and other statuses are very rare, showing the platform's reliability.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Delivered Orders %", f"{(filtered_orders['order_status'] == 'delivered').mean() * 100:.2f}%")
    col2.metric("Cancelled Orders %", f"{(filtered_orders['order_status'] == 'canceled').mean() * 100:.2f}%")
    col3.metric("Other Statuses %", f"{(~filtered_orders['order_status'].isin(['delivered', 'canceled'])).mean() * 100:.2f}%")


st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Monthly Order Volume Trends</h2>""", unsafe_allow_html=True)

monthly_counts = filtered_orders.groupby(filtered_orders['order_purchase_timestamp'].dt.to_period('M')).size().reset_index()
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
if selected_year == 'All' or selected_year == 2017:
    fig.add_annotation(
        x=monthly_counts[monthly_counts['month'] == '05-2017'].iloc[0]['month'],
        y=monthly_counts['order_count'].max() * 0.55,
        text="Consistent Growth in Usage",
        font=dict(color="Lime", size=16),
        showarrow=True
    )
if selected_year == 'All' or selected_year == 2017:
    fig.add_annotation(
        x=monthly_counts['month'].iloc[monthly_counts['order_count'].idxmax()],
        y=monthly_counts['order_count'].max(),
        text="Black Friday Peak",
        font=dict(color="orange", size=16),
        showarrow=True,
        xshift=-10
    )
if selected_year == 'All' or selected_year == 2018:
    fig.add_annotation(
        x=monthly_counts[monthly_counts['month'] == '01-2018'].iloc[0]['month'],
        y=monthly_counts['order_count'].max(),
        text="Carnival Peak",
        font=dict(color="Yellow", size=16),
        showarrow=True,
        yshift=-12
    )
if selected_year == 'All' or selected_year == 2018:
    fig.add_annotation(
        x=monthly_counts[monthly_counts['month'] == '05-2018'].iloc[0]['month'],
        y=monthly_counts['order_count'].max(),
        text="Decrease in Rainy Season",
        font=dict(color="blue", size=16),
        showarrow=True,
        xshift=-10
    )
st.plotly_chart(fig)

with st.expander("Monthly Order Trends Summary"):
    st.markdown("- Monthly order volumes increases consistently in beginning months of 2017, showing growth in platform's usage.")
    st.markdown("- Big spike in order volume during peak festive months like Carnival & events like Black Friday.")
    st.markdown("- Slow decrease after New Year is due to Rainy Season. Seasonal demand drives these peaks.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Peak Month", monthly_counts.loc[monthly_counts['order_count'].idxmax(), 'month'])
    col2.metric("% Increase During Peak", f"{(((monthly_counts.loc[monthly_counts['order_count'].idxmax(), 'order_count'] - monthly_counts.loc[monthly_counts['order_count'].idxmax() - 1, 'order_count']) / monthly_counts.loc[monthly_counts['order_count'].idxmax() - 1, 'order_count']) * 100):.1f}%")
    col3.metric("Avg Orders Per Month", f"{monthly_counts['order_count'].mean():,.0f}")

# delivery time Analysis
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Delivery Time Analysis</h2>""", unsafe_allow_html=True)

x_values = pd.to_numeric(filtered_orders["delivery_time_gap_hrs"], errors="coerce").dropna()

fig = px.histogram(x=x_values, nbins=50, opacity=0.6, color_discrete_sequence=["#636EFA"])

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

st.markdown("<span style='font-weight:bold; font-size:1.2rem;'>Key KPIs for Delivery Time</span>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Early Delivered Orders (%)", f"{(x_values > 12).mean() * 100:.1f}%")
col2.metric("Late Delivered Orders (%)", f"{(x_values < -12).mean() * 100:.1f}%")
col3.metric("Delivered on Estimated Day (%)", f"{(x_values.between(-12,12)).mean() * 100:.1f}%")
col4.metric("Average Delivery Time (hrs)", f"{x_values.mean():.2f}")

with st.expander("Delivery Time Analysis Summary"):
    st.markdown("- Most orders arrive well before estimated delivery dates.")
    st.markdown("- A big part of orders are delivered very early, showing requirement of improvement in estimation of delivery dates.")
    st.markdown("- Late deliveries are rare, indicating good logistics performance.")

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Order Status Time Gap Analysis</h2>""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4.5, 4.5])
bin_count = col1.slider("Number of bins:", min_value=5, max_value=100, value=20, step=1)
fig = px.histogram(
    filtered_orders,
    x=filtered_orders['purchase_to_approval_hours'],
    nbins=bin_count,
    title="Order Approval Time Distribution",
    template="plotly_white",
    marginal="box",
    opacity=0.6,
    color_discrete_sequence=["#C363FA"],
)
fig.update_layout(
    xaxis_title="Order Purchase to Approval Time (hours)",
    yaxis_title="Number of Orders",
    bargap=0.05,
    title_x=0.5
)
fig.update_traces(marker_line_width=1, marker_line_color="white")
col2.plotly_chart(fig)

fig = px.histogram(
    filtered_orders,
    x=filtered_orders[filtered_orders['approval_to_delivery_hours'] >= 0]['approval_to_delivery_hours'],
    nbins=bin_count,
    title="Order Delivery Time Distribution",
    template="plotly_white",
    marginal="box",
    opacity=0.6,
    color_discrete_sequence=["#63FAED"]
)
fig.update_layout(
    xaxis_title="Order Approval to Delivery Time (hours)",
    yaxis_title="Number of Orders",
    bargap=0.05,
    title_x=0.5
)
fig.update_traces(marker_line_width=1, marker_line_color="white")
col3.plotly_chart(fig)

with st.expander("Order Status Time Gap Summary"):
    st.markdown("- Most orders are approved very quickly (less than 10 hours), showing efficient processing but has room for improvement, may be automated.")
    st.markdown("- Approval-to-delivery timelines are fairly good, and show expected minor outliers.")
    st.markdown("- Again, there is a lot of room for improvement in logistics for approval-to-delivery time.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Purchase→Approval (hrs)", f"{filtered_orders['purchase_to_approval_hours'].mean():.1f}")
    col2.metric("Avg Approval→Delivery (hrs)", f"{filtered_orders['approval_to_delivery_hours'].mean():.1f}")
    col3.metric("% Approvals < 1 hr", f"{(filtered_orders['purchase_to_approval_hours'] < 1).mean() * 100:.1f}%")