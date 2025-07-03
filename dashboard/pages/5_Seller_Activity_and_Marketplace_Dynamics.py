import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scripts.utils import expander_styles, get_state_code_names, get_region_states, get_category_map
from scripts.data_cleaning import import_data
from collections import defaultdict

# configuring page
st.set_page_config(page_title="Seller Activity & Marketplace - EDA", page_icon="🛍️", initial_sidebar_state="expanded", layout='wide')
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
filtered_payments = payments[payments["order_id"].isin(filtered_orders["order_id"])]

# mapping tool for customer by region
state_to_region = {
    state: region
    for region, states in region_states_dict.items()
    for state in states
}
filtered_customers["customer_region"] = filtered_customers["customer_state"].map(state_to_region)

# mapping tool for product category by group
category_map = get_category_map()
filtered_products["product_group_name"] = filtered_products["product_category_name"].map(category_map)

# merged DFs
customers_orders = filtered_orders.merge(filtered_customers, on="customer_id")
cust_orders_items = customers_orders.merge(filtered_order_items, on="order_id")
products_order_items = filtered_order_items.merge(filtered_products, on="product_id")
products_items_orders = products_order_items.merge(filtered_orders, on="order_id")
payments_order_items = payments.merge(filtered_order_items, on="order_id")
payments_orders = payments.merge(filtered_orders, on="order_id")
payments_items_delivery_time = payments_order_items.merge(orders[['order_id', 'order_delivered_timestamp']], on='order_id', how='left')


# for this one:
@st.cache_data
def compute_plotting_dfs():
    orders_by_products = products_items_orders.groupby("product_id")["order_id"].count().reset_index().rename(columns={'order_id':'orders_count'})
    orders_by_products = orders_by_products.sort_values(by="orders_count", ascending=False)

    orders_by_sellers = filtered_order_items.groupby("seller_id")["order_id"].count().reset_index().rename(columns={'order_id':'orders_count'})
    orders_by_sellers = orders_by_sellers.sort_values(by="orders_count", ascending=False)
    products_by_sellers = filtered_order_items.groupby("seller_id")["product_id"].nunique().reset_index().rename(columns={'product_id':'products_count'})
    products_by_sellers = products_by_sellers.sort_values(by="products_count", ascending=False)
    sellers_by_products = filtered_order_items.groupby("product_id")["seller_id"].nunique().reset_index().rename(columns={'seller_id':'sellers_count'}).sort_values(by="sellers_count", ascending=False)
    products_by_seller_count = sellers_by_products.groupby("sellers_count")["product_id"].count().reset_index().sort_values(by="product_id", ascending=False)

    revenue_by_sellers = payments_order_items.groupby("seller_id")["payment_value"].sum().reset_index()
    revenue_by_sellers = revenue_by_sellers.sort_values(by="payment_value", ascending=False)

    sellers_by_categories = products_order_items.groupby("product_category_name")["seller_id"].nunique().reset_index().rename(columns={'seller_id':'sellers_count'}).sort_values(by="sellers_count",ascending=False)

    return (orders_by_products,orders_by_sellers,products_by_sellers,sellers_by_products,products_by_seller_count,revenue_by_sellers,sellers_by_categories)


(   orders_by_products,
    orders_by_sellers,
    products_by_sellers,
    sellers_by_products,
    products_by_seller_count,
    revenue_by_sellers,
    sellers_by_categories) = compute_plotting_dfs()



# dashboard content
st.title("Seller Activity & Marketplace Analysis")
st.markdown("""
This section explores how sellers contribute to the platform – their volume, diversity, and dominance.
We analyze how products are spread across sellers, identify high performers, and highlight market balance or concentration.
<p style='font-style:italic; margin-top:-8px; font-weight:700;'>Note: Use side bar for filters</p>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Number of Unique Sellers", f"{filtered_order_items["seller_id"].nunique():,}")
col2.metric("Avg Products per Seller", f"{products_by_sellers["products_count"].mean():.2f}")
col3.metric("Avg Number of Orders per Seller", f"{filtered_order_items.groupby("seller_id")["order_id"].count().mean():.2f}")

st.divider()
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Order Volume & Revenue by Sellers</h2>""", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 3, 1])
n = col2.slider(
    f"Select Number of Top Sellers to show:",
    min_value=1,
    max_value=50,
    value=20,
)
selected_quantity = col4.selectbox(
    "Quantity to compare by Sellers:",
    options=["Number of Orders", "Total Revenue"],
    index=0
)

if selected_quantity == "Number of Orders":
    col1, col2 = st.columns(2)
    fig = px.bar(
        orders_by_sellers.head(n),
        x='seller_id',
        y='orders_count',
        color='seller_id',
        title=f"Number of Orders by Sellers (Top {n})",
        text='orders_count',
        labels={'seller_id': 'Sellers', 'orders_count': 'Number of Orders'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

    with st.expander("Top Sellers Performance by Order Volume Summary"):
        st.markdown("""- Some top sellers (brands and commercial) do dominate & top 10 contribute to 13.6% of total orders.
                    - Dependent but not super dependent on top sellers, as most sellers do get less than 100/200 orders.
                    - Fix this later.""")
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Top {n} Sellers Contribution in Total", f"{(orders_by_sellers.head(n)["orders_count"].sum()/orders_by_sellers["orders_count"].sum()) * 100:.2f} %")
        col2.metric("No. of Sellers with >100 orders", f"{orders_by_sellers[orders_by_sellers['orders_count'] > 100]["seller_id"].nunique()}")
        col3.metric("No. of Sellers with <= 10 orders", f"{orders_by_sellers[orders_by_sellers['orders_count'] <= 10]["seller_id"].nunique()}")

elif selected_quantity == "Total Revenue":
    col1, col2 = st.columns(2)
    fig = px.bar(
        revenue_by_sellers.head(n),
        x='seller_id',
        y='payment_value',
        color='seller_id',
        title=f"Total Revenue by Sellers (Top {n})",
        text='payment_value',
        labels={'seller_id': 'Sellers', 'payment_value': 'Total Seller Revenue'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

    with st.expander("Top Sellers Performance by Revenue Summary"):
        st.markdown("""- Some top sellers (brands and commercial) do dominate & top 10 contribute to 13.6% of total orders.
                    - Dependent but not super dependent on top sellers, as most sellers do get less than 100/200 orders.
                    - Fix this later.""")
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Top {n} Sellers Contribution in Total", f"{(revenue_by_sellers.head(n)["payment_value"].sum()/revenue_by_sellers["payment_value"].sum()) * 100:.2f} %")
        col2.metric(f"No. of Sellers in both Top {n} list", len(set(orders_by_sellers.head(n)["seller_id"]) & set(revenue_by_sellers.head(n)["seller_id"])))
        col3.metric("No. of Sellers with <= 1M Revenue", f"{revenue_by_sellers[revenue_by_sellers['payment_value'] <= 1000000]["seller_id"].nunique()}")

st.divider()
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Products Volume Distribution by Sellers</h2>
            """, unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([2, 4, 3, 1])
n = col2.slider(
    "Select the number of sellers to show:",
    min_value=10,
    max_value=50,
    value=20
)
fig = px.bar(
    products_by_sellers.head(n),
    x="seller_id",
    y="products_count",
    color="seller_id",
    title=f"Top {n} Sellers by Unique Products",
    text='products_count',
    labels={'seller_id': 'Seller', 'products_count': 'Number of Unique Products'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig)
with st.expander(f"Top {n} Sellers by Unique Products Summary"):
    st.markdown("Some stuff bout it")
    col1, col2, col3 = st.columns(3)
    col1.metric("No. of Specialist Sellers [<10 products]", products_by_sellers[products_by_sellers["products_count"] < 10]["seller_id"].nunique())
    col2.metric("No. of Generalist Sellers [>50 products]", products_by_sellers[products_by_sellers["products_count"] > 50]["seller_id"].nunique())
    col3.metric("Revenue Ratio (Generalists/Specialists)", f"{revenue_by_sellers[revenue_by_sellers["seller_id"].isin(products_by_sellers[products_by_sellers["products_count"] > 50]["seller_id"])]["payment_value"].mean() / revenue_by_sellers[revenue_by_sellers["seller_id"].isin(products_by_sellers[products_by_sellers["products_count"] < 10]["seller_id"])]["payment_value"].mean():.2f}")

st.divider()

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Sellers for Unique Product Distribution</h2>
            """, unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([2, 4, 3, 1])
n = col2.slider(
    "Select the number of products to show:",
    min_value=10,
    max_value=50,
    value=20
)
fig = px.bar(
    products_by_seller_count[products_by_seller_count["sellers_count"] > 1],
    y="product_id",
    x="sellers_count",
    color="sellers_count",
    title=f"Top {n} Products by Unique Sellers",
    text='sellers_count',
    labels={'product_id': 'Product', 'sellers_count': 'Number of Unique Sellers'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig)
with st.expander(f"Top {n} Products by Unique Sellers Summary"):
    st.markdown("Some stuff bout it")
    col1, col2, col3 = st.columns(3)
    col1.metric("No. of Products sold by > 1 sellers", f"{len(sellers_by_products[sellers_by_products["sellers_count"] > 1])} ({len(sellers_by_products[sellers_by_products["sellers_count"] > 1])/len(sellers_by_products)*100:.2f} %)")
    col2.metric("Products sold by > 3 Sellers", f"{len(sellers_by_products[sellers_by_products["sellers_count"] > 3])}")
    col3.metric("Orders for Multi-Sellers Products", f"{orders_by_products[orders_by_products["product_id"].isin(sellers_by_products[sellers_by_products["sellers_count"] > 1]["product_id"])]["orders_count"].sum()} ({orders_by_products[orders_by_products["product_id"].isin(sellers_by_products[sellers_by_products["sellers_count"] > 1]["product_id"])]["orders_count"].sum()/len(filtered_orders) * 100:.2f} %)")
st.divider()

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Unique Sellers by Category:</h2>
            <p style="height:1.2rem;"></p>
            """, unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
col2.metric("No of Sellers in 'toys' Category", f"{sellers_by_categories[sellers_by_categories["product_category_name"] == 'toys']["sellers_count"].iloc[0]} ({sellers_by_categories[sellers_by_categories["product_category_name"] == 'toys']["sellers_count"].iloc[0]/filtered_order_items["seller_id"].nunique() * 100 :.2f}%)")
col3.metric("Avg No of Sellers in a Category", f"{sellers_by_categories["sellers_count"].mean():.2f}")
col4.metric("Avg No of Sellers in a category [excluding toys]", f"{sellers_by_categories[sellers_by_categories["product_category_name"] != 'toys']["sellers_count"].mean():.2f}")
