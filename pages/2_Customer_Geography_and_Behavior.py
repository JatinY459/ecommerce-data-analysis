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
@st.cache_data
def compute_plotting_dfs():
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

    return (customers_by_region, customers_by_state, cust_orders_delivery_time_by_region, ship_price_by_state, ship_price_by_region)

(customers_by_region, 
 customers_by_state, 
 cust_orders_delivery_time_by_region, 
 ship_price_by_state, 
 ship_price_by_region) = compute_plotting_dfs()


# dashboard content
st.title("Customer Geography and Behavior Analysis")
st.markdown("""
This page explores where customers come from, their order patterns, and regional influences on logistics and engagement.  
Understand the trends and behavior in key markets and delivery challenges.  
<p style='font-style:italic; margin-top:-8px; font-weight:700;'>Note: Use side bar for filters</p>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Unique Customers Ids", f"{filtered_customers.shape[0]:,}")
col2.metric("Cities with Orders", f"{(filtered_customers['customer_city'].nunique())}")
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
    st.markdown("""- The **South-East region dominates order volume**, accounting for around 69% of total orders, driven by economically strong states like SP, RJ, and MG.
- The **North region contributes just 1.8%**, reflecting its less population and poor infrastructure.
- The distribution shows clear **regional concentration** of e-commerce usage in urban hubs.""")
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    col2.metric("highest volume region to second highest", f"{(customers_by_state.iloc[0]["orders_count"]/customers_by_state.iloc[1]["orders_count"]) * 100:.2f} %")
    col3.metric("highest volume region to lowest", f"{(customers_by_state.iloc[0]["orders_count"]/customers_by_state.iloc[-1]["orders_count"]) * 100:.2f} %")

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
    st.markdown("""
- The treemap reinforces that **SP, RJ, and MG are the top-performing states**, leading order volume significantly.
- Northern states like RR, AC, and AP combined contribute just **0.02% of total orders**.
- Federal District (DF) despite being very small contributes about 2% of total orders due to its administrative importance.
    """)
    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 3, 1])
    col2.metric("Top 3 States Combined %", f"{(customers_by_state.head(3)['orders_count'].sum()) / (customers_by_state['orders_count'].sum()) * 100:.2f} %")
    col3.metric("Bottom 3 Contributing States Combined %", f"{(customers_by_state.tail(3)['orders_count'].sum()) / (customers_by_state['orders_count'].sum()) * 100:.2f} %")
    col4.metric("Orders from Least Contributing States", f"{customers_by_state.tail(3)['orders_count'].sum()}")

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

with st.expander("Region-Wise Order Distribution Summary"):
    st.markdown("""
- **Only 3 states cross 5,000 orders**, emphasizing the strong reliance on key regions.
- 12 states surpass the 1,000 order mark, showing **limited platform reach across Brazil**.
- Majority of states contribute normally, highlighting opportunity for regional expansion.
""")
    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 3, 1])
    col2.metric("No. of States with > 5k orders", len(customers_by_state[customers_by_state["orders_count"] > 5000]))
    col3.metric("No. of States with > 1k orders", len(customers_by_state[customers_by_state["orders_count"] > 1000]))
    col4.metric("States with Least Orders", f"{customers_by_state.iloc[-1]['customer_state']}, {customers_by_state.iloc[-2]['customer_state']}, {customers_by_state.iloc[-3]['customer_state']}")

col1, col2 = st.columns(2)
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
        color="customer_city",
        hole=0.4
    ).update_traces(textposition='inside', hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}")
)
with col1.expander("Avg Delivery Time by Region Summary"):
    st.markdown("""
- The **North region has the longest average delivery time at ~15 days**, due to remoteness and logistical challenges.
- South-East and North-East regions show **faster delivery, averaging around 11 days**.
- Indicates room to improve service levels and aim for delivery in a week, for key regions.
""")
    st.metric("Slowest Delivery Region", f"{cust_orders_delivery_time_by_region.iloc[-1]['customer_region']}, ~{int(cust_orders_delivery_time_by_region['avg_delivery_time'].max()//24)} days")

with col2.expander("Top 10 Cities by Number of Orders Summary"):
    st.markdown("""
- The **top 10 cities contribute to ~35% of the total orders**, indicating a strong urban demand.
- In these economic centres, **São Paulo** leads significantly, followed by **Rio de Janeiro** and **Belo Horizonte**.
- These cities individually account for thousands of orders, implying high demand & opportunity for betterment in logistics here.
""")
    st.metric("Contribution of Top 10 cities in Total Orders", f"{filtered_customers.groupby("customer_city")["customer_id"].nunique().reset_index().rename(columns={"customer_id": "orders_count"}).sort_values("orders_count", ascending=False).head(10)['orders_count'].sum() / filtered_customers['customer_id'].nunique() * 100:.2f}%")

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
    st.markdown("""
- Most states show consistent mean shipping price around **42**.
- North/North-East states exhibit **higher shipping charges**, reflecting logistic challenges.
- Roraima (RR) shows lowest shipping cost, it is likely a skewed result, as it has only 34 orders.
""")
    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 3, 1])
    col2.metric("Mean Shipping Price", f"{cust_orders_items['shipping_charges'].mean():.2f}")
    col3.metric("Highest Mean Shipping Price State", f"{ship_price_by_state.iloc[0]['customer_state']}, {ship_price_by_state['avg_shipping_charges'].max():.2f}")
    col4.metric("Lowest Mean Shipping Price State", f"{ship_price_by_state.iloc[-1]['customer_state']}, {ship_price_by_state['avg_shipping_charges'].min():.2f}")

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
    st.markdown("""
- North and North-East regions have the **highest average shipping prices (47, 45)**.
- South, South-East, and Mid-West are **more cost-efficient (~41-42)**.
- Highlights potential for cost optimization in remote regions. And opportunity to reduce costs in high volume regions too.
""")
with col2.expander("Shipping-Charges by Region Summary"):
    st.markdown("""
- Outliers with **very high shipping prices** exist, but are rare compared to total orders.
- 75% of shipping costs stay below **56 in most regions**, slightly higher (59 & 61) in North/North-East.
- North shows **highest median shipping price at 39** (in North region), with overall median near 35.
""")
