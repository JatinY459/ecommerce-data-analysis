import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scripts.utils import expander_styles, get_state_code_names, get_region_states
from scripts.data_cleaning import import_data

# configuring page
st.set_page_config(page_title="Customer Geography & Behavior - EDA", page_icon="👤", initial_sidebar_state="expanded", layout='wide')
# importing data
orders, order_items, customers, payments, products = import_data(dashboard=True)
state_names_dict = get_state_code_names()
region_states_dict = get_region_states()
# filter
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year:", options=[2017, 2018, 'All'], index=2)
selected_order_status = st.sidebar.multiselect(
    "Select Order Status:",
    options=["delivered", "shipped", "canceled", "approved", "processing", "invoiced"],
    default=["delivered", "shipped", "canceled", "approved", "processing", "invoiced"]
)
selected_regions = st.sidebar.multiselect(
    "Select Region:",
    options=list(region_states_dict.keys()),
    default=list(region_states_dict.keys())
)
selected_states = [state for region in selected_regions for state in region_states_dict[region]]

# TODO: see if these filters are needed or not
filtered_orders = orders[orders["order_purchase_timestamp"].dt.year == int(selected_year)] if selected_year != 'All' else orders
filtered_orders = filtered_orders[filtered_orders["order_status"].isin(selected_order_status)]

# TODO: see if i can filter customers based on filtered orders
filtered_customers = customers[customers["customer_id"].isin(filtered_orders["customer_id"])]
filtered_customers = filtered_customers[filtered_customers["customer_state"].isin(selected_states)]


# mapping tool for customer by region
state_to_region = {
    state: region
    for region, states in region_states_dict.items()
    for state in states
}
filtered_customers["customer_region"] = filtered_customers["customer_state"].map(state_to_region)
customers_orders = filtered_orders.merge(filtered_customers, on="customer_id")
cust_orders_items = customers_orders.merge(order_items, on="order_id")

# resources
customers_by_region = filtered_customers.groupby("customer_region")["customer_id"].nunique().reset_index().rename(columns={"customer_id": "orders_count"})
customers_by_region = customers_by_region.sort_values(by="orders_count", ascending=False)
customers_by_state = filtered_customers.groupby('customer_state')['customer_id'].nunique().reset_index().rename(columns={'customer_id': 'orders_count'})
customers_by_state = customers_by_state.sort_values(by="orders_count", ascending=False)
cust_orders_delivery_time_by_region = customers_orders.groupby("customer_region")["delivery_time_gap_hrs"].mean().reset_index().rename(columns={"delivery_time_gap_hrs": "avg_delivery_time"})
cust_orders_delivery_time_by_region["avg_delivery_time"] = cust_orders_delivery_time_by_region["avg_delivery_time"].round(2)
cust_orders_delivery_time_by_region = cust_orders_delivery_time_by_region.sort_values(by="avg_delivery_time")
ship_price_by_state = cust_orders_items.groupby("customer_state")["shipping_charges"].mean().reset_index().rename(columns={"shipping_charges": "avg_shipping_charges"})
ship_price_by_state = ship_price_by_state.sort_values(by="avg_shipping_charges", ascending=False)
ship_price_by_region = cust_orders_items.groupby("customer_region")["shipping_charges"].mean().reset_index().rename(columns={"shipping_charges": "avg_shipping_charges"})
ship_price_by_region = ship_price_by_region.sort_values(by="avg_shipping_charges", ascending=False)

# dashboard content
st.title("Customer Geography and Behavior Analysis")
st.markdown("""
This page explores where customers come from, their order patterns, and regional influences on logistics and engagement.  
Gain insights into key markets and delivery challenges.  
<p style='font-style:italic; margin-top:-8px;'>*Use side bar for filters</p>
""", unsafe_allow_html=True)
st.markdown("**customer_id* is not a unique identifier for customers, hence customer lack unique id in this dataset.")
st.markdown("<p style='font-style:italic;'>Click on legend items or bars to filter specific order statuses for better visibility.*</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Total Unique Customers Ids", f"{filtered_customers.shape[0]:,}")
col2.metric("Cities Reached", f"{(filtered_customers['customer_city'].nunique())}")
col3.metric("Top State", f"{customers_by_state.loc[customers_by_state['orders_count'].idxmax(), 'customer_state']} ({state_names_dict[customers_by_state.loc[customers_by_state['orders_count'].idxmax(), 'customer_state']]})")

col1, col2 = st.columns(2)
fig = px.bar(
    customers_by_region,
    x="customer_region",
    y="orders_count",
    color="customer_region",
    title="Region-Wise Order Distribution",
    text='orders_count',
    labels={'customer_region': 'Region', 'orders_count': 'Number of Orders'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col1.plotly_chart(fig)

fig = px.pie(
    customers_by_region,
    names='customer_region',
    values='orders_count',
    title='Region Orders Distribution',
    labels={'customer_region': 'Region', 'orders_count': 'Number of Orders'},
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}")
col2.plotly_chart(fig)

with st.expander("Region-Wise Order Distribution Summary"):
    st.markdown("write content here, and METRICS/KPIs")

agg_df = filtered_customers.groupby(["customer_region", "customer_state"]).agg(order_count=("customer_id", "count")).reset_index()
fig = px.treemap(
    agg_df,
    path=["customer_region", "customer_state"],
    values="order_count",
    title="Orders Volume by Region & State Treemap",
    color="order_count",
    color_continuous_scale=px.colors.sequential.Sunsetdark,
)
fig.update_traces(
    textinfo="label+value+percent parent",
    hovertemplate="<b>%{label}</b><br>Orders: %{value}<br>% of Parent: %{percentParent:.2%}<br>% of Total: %{percentRoot:.2%}<extra></extra>"
)
fig.update_layout(
    title_x=0.4,
    margin=dict(t=50, l=25, r=25, b=25),
    font=dict(size=14),
    coloraxis_colorbar=dict(title="Order Count")
)
st.plotly_chart(fig)
with st.expander("Region & State Orders Volume Summary"):
    st.markdown("write content here, and METRICS/KPIs")

# st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Bar Plot for State-wise Order Distribution</h2>""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
fig = px.bar(
    customers_by_state.head(len(selected_states) // 2),
    x="customer_state",
    y="orders_count",
    color="customer_state",
    title="State-Wise Order Distribution Top Half",
    text='orders_count',
    labels={'customer_state': 'State', 'orders_count': 'Number of Orders'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col1.plotly_chart(fig)

fig = px.bar(
    customers_by_state.tail((len(selected_states) // 2) + 1),
    x="customer_state",
    y="orders_count",
    color="customer_state",
    title="State-Wise Order Distribution Bottom Half",
    text='orders_count',
    labels={'customer_state': 'State', 'orders_count': 'Number of Orders'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col2.plotly_chart(fig)

with col1.expander("Region-Wise Order Distribution Summary"):
    st.markdown("write content here, and METRICS/KPIs")
with col2.expander("State-Wise Order Distribution Summary"):
    st.markdown("write content here, and METRICS/KPIs")

col1, col2 = st.columns([1,1])
col1.plotly_chart(
    px.bar(
        cust_orders_delivery_time_by_region,
        x="customer_region",
        y="avg_delivery_time",
        color="customer_region",
        title="Region-Wise Avg Delivery Time Distribution",
        text='avg_delivery_time',
        labels={'customer_region': 'Region', 'avg_delivery_time': 'Average Delivery Time (hrs)'}
    ).update_traces(textposition='outside').update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
)
col2.plotly_chart(
    px.pie(
        filtered_customers.groupby("customer_city")["customer_id"].nunique().reset_index().rename(columns={"customer_id": "orders_count"}).sort_values("orders_count", ascending=False).head(10),
        names="customer_city",
        values="orders_count",
        title="Top 10 Cities by Number of Orders",
        labels={"customer_city": "City", "orders_count": "Number of Orders"},
        color="customer_city"
    )
)
with col1.expander("Avg Delivery Time by Region Summary"):
    st.markdown("write content here, and METRICS/KPIs")
with col2.expander("Top 10 Cities by Number of Orders Summary"):
    st.markdown("write content here, and METRICS/KPIs")


# st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Shipping Price Patterns by Region & State</h2>""", unsafe_allow_html=True)
fig = px.bar(
    ship_price_by_state,
    x="customer_state",
    y="avg_shipping_charges",
    color="customer_state",
    title="State-Wise Shipping Price Distribution",
    text='avg_shipping_charges',
    labels={'customer_state': 'State', 'avg_shipping_charges': 'Average Shipping Price'}
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig)
with st.expander("Shipping Price Distribution by State Summary"):
    st.markdown("write content here, and METRICS/KPIs")


col1, col2 = st.columns([1, 1])
fig = px.bar(
    ship_price_by_region,
    x="customer_region",
    y="avg_shipping_charges",
    color="customer_region",
    text='avg_shipping_charges',
    title="Region-Wise Shipping Price Distribution",
    labels={'customer_region': 'Region', 'avg_shipping_charges': 'Average Shipping Price'},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col1.plotly_chart(fig)

fig = px.box(
    cust_orders_items,
    x="customer_region",
    y="shipping_charges",
    color="customer_region",
    title="Shipping-Charges by Region",
    points="outliers",
    template="plotly_white"
)
fig.update_layout(
    xaxis_title="Customer Region",
    yaxis_title="Shipping Charges",
    showlegend=False,
    title_x=0.5,
    font=dict(size=14)
)
col2.plotly_chart(fig)

with col1.expander("Shipping Price Patterns Summary"):
    st.markdown("write content here, and METRICS/KPIs")
with col2.expander("Shipping-Charges by Region Summary"):
    st.markdown("write content here, and METRICS/KPIs")
