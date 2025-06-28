import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scripts.utils import expander_styles, get_state_code_names, get_region_states
from scripts.data_cleaning import import_data

# configuring page
st.set_page_config(page_title="Product & Category - EDA", page_icon="🛍️", initial_sidebar_state="expanded", layout='wide')
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

filtered_order_items = order_items[order_items["order_id"].isin(filtered_orders["order_id"])]
filtered_products = products[products["product_id"].isin(filtered_order_items["product_id"])]

# mapping tool for customer by region
state_to_region = {
    state: region
    for region, states in region_states_dict.items()
    for state in states
}
filtered_customers["customer_region"] = filtered_customers["customer_state"].map(state_to_region)

# merged DFs
customers_orders = filtered_orders.merge(filtered_customers, on="customer_id")
cust_orders_items = customers_orders.merge(filtered_order_items, on="order_id")
products_order_items = filtered_order_items.merge(filtered_products, on="product_id")

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

# for this one:
products_by_category = filtered_products.groupby("product_category_name")["product_id"].nunique().reset_index().rename(columns={"product_id": "products_count"})
products_by_category = products_by_category.sort_values(by="products_count", ascending=False)

products_price_by_category = products_order_items.groupby("product_category_name")["price"].mean().reset_index()
products_price_by_category = products_price_by_category.sort_values(by="price", ascending=False)

# dashboard content
st.title("Product & Category Analysis")
st.markdown("""
This section explores the landscape of products and categories in the e-commerce platform.  
We examine category popularity, pricing patterns, and product specifications (weight, dimensions), revealing inventory and logistics implications.
<p style='font-style:italic; margin-top:-8px; font-weight:700;'>Note: Use side bar for filters</p>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Product Categories", f"{filtered_products['product_category_name'].nunique():,}")
col2.metric("Number of Unique Products", f"{filtered_products['product_id'].nunique():,}")
col3.metric("Avg Product Price", f"{filtered_order_items['price'].mean():,.2f}")

st.plotly_chart(
    px.histogram(
        filtered_order_items,
        x="price",
        nbins=50,
        title="Product Price Distribution",
        labels={"price": "Product Price"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    ).update_layout(
        xaxis_title="Product Price",
        yaxis_title="Count",
        title_x=0.5,
        font=dict(size=14),
        bargap=0.1,
        bargroupgap=0.1,
        xaxis=dict(tickformat=',.0f', ticks='outside', showline=True, linewidth=1, linecolor='black'),
        yaxis=dict(ticks='outside', showline=True, linewidth=1, linecolor='black')
    )
)

col1, col2 = st.columns(2)

fig = px.bar(
    products_by_category.head(5),
    x="product_category_name",
    y="products_count",
    color="product_category_name",
    title="Category-Wise Product Distribution (Top 5)",
    text='products_count',
    labels={'product_category_name': 'Category', 'products_count': 'Number of Products'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col1.plotly_chart(fig)

fig = px.pie(
    pd.concat([products_by_category.head(5), pd.DataFrame({'product_category_name': ['Others'], 'products_count': [products_by_category['products_count'].sum() - products_by_category.head(5)['products_count'].sum()]})]),
    names='product_category_name',
    values='products_count',
    title='Product Categories Top 5 vs Others',
    labels={'product_category_name': 'Category', 'products_count': 'Number of Products'},
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}")
col2.plotly_chart(fig)

with st.expander("Products Categories Top 5 vs Others Summary"):
    st.markdown("""Write the summaries & Metrics/KPIs here""")
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean no. of Products [Including Toys]", f"{products_by_category['products_count'].mean():.2f}")
    col2.metric("Mean no. of Products [Excluding Toys]", f"{products_by_category[products_by_category['product_category_name'] !='toys']['products_count'].mean():.2f}")

# category distro
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Product Categories Distribution</h2>
            Options:""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
category_view = col2.radio(
    "View Categories by Product Count",
    options=["Top N", "Bottom N"],
    index=0,
    horizontal=True
)
n = col3.slider(
    f"Select number of categories to display",
    min_value=1,
    max_value=min(35, 69),
    value=20
)
if category_view == "Top N":
    fig = px.bar(
        products_by_category.iloc[1:n+1],
        x="product_category_name",
        y="products_count",
        color="product_category_name",
        title=f"Product Categories Distribution (Top {n}) [Excluding Toys]",
        text='products_count',
        labels={'product_category_name': 'Category', 'products_count': 'Number of Products'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

if category_view == "Bottom N":
    fig = px.bar(
        products_by_category.iloc[-n:-1],
        x="product_category_name",
        y="products_count",
        color="product_category_name",
        title=f"Product Categories Distribution (Bottom {n})",
        text='products_count',
        labels={'product_category_name': 'Category', 'products_count': 'Number of Products'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

with st.expander("Top Product Categories Distribution Summary"):
    st.markdown("""Write the summaries & Metrics/KPIs here""")
    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 3, 1])
    col2.metric("Mean number of Products (filtered view)", f"{products_by_category.iloc[1:n+1]["products_count"].mean() if category_view=="Top N" else products_by_category.iloc[-n:-1]["products_count"].mean():.2f}")
    col3.metric("Categories with < 10 Products", len(products_by_category[products_by_category['products_count'] < 10]))
    col4.metric("Categories with > 100 Products", f"{len(products_by_category[products_by_category['products_count'] > 100])}")

# st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Bar Plot for State-wise Order Distribution</h2>""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
fig = px.bar(
    products_price_by_category.head(10),
    x="product_category_name",
    y="price",
    color="product_category_name",
    title="Category Price Distribution Top Half",
    text='price',
    labels={'product_category_name': 'Category', 'price': 'Price'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col1.plotly_chart(fig)

fig = px.bar(
    products_price_by_category.tail(10),
    x="product_category_name",
    y="price",
    color="product_category_name",
    title="Category Price Distribution Bottom Half",
    text='price',
    labels={'product_category_name': 'Category', 'price': 'Price'},
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
