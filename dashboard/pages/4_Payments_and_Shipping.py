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

# for this one:
products_by_category = filtered_products.groupby("product_category_name")["product_id"].nunique().reset_index().rename(columns={"product_id": "products_count"})
products_by_category = products_by_category.sort_values(by="products_count", ascending=False)
products_by_group = filtered_products.groupby("product_group_name")["product_id"].nunique().reset_index().rename(columns={"product_id": "products_count"})
products_by_group = products_by_group.sort_values(by="products_count", ascending=False)

products_price_by_category = products_order_items.groupby("product_category_name")["price"].mean().reset_index()
products_price_by_category = products_price_by_category.sort_values(by="price", ascending=False)
products_price_by_group = products_order_items.groupby("product_group_name")["price"].mean().reset_index()
products_price_by_group = products_price_by_group.sort_values(by="price", ascending=False)

shipping_price_by_group = products_order_items.groupby("product_group_name")["shipping_charges"].mean().reset_index()
shipping_price_by_group = shipping_price_by_group.sort_values(by="shipping_charges", ascending=False)
delivery_time_by_group = products_items_orders.groupby("product_group_name")["delivery_time_gap_hrs"].mean().reset_index()
delivery_time_by_group = delivery_time_by_group.sort_values(by="delivery_time_gap_hrs", ascending=False)
product_weight_by_group = filtered_products.groupby("product_group_name")["product_weight_g"].mean().reset_index()
product_weight_by_group = product_weight_by_group.sort_values(by="product_weight_g", ascending=False)
product_volume_by_group = filtered_products.groupby("product_group_name")["product_volume_cm3"].mean().reset_index()
product_volume_by_group = product_volume_by_group.sort_values(by="product_volume_cm3", ascending=False)

payments_by_type = filtered_payments.groupby("payment_type")["order_id"].count().reset_index().rename(columns={'order_id': 'payments_count'})
payments_by_type = payments_by_type.sort_values(by="payments_count", ascending=False)

no_of_installments = filtered_payments[filtered_payments['payment_type'] == "credit_card"].groupby("payment_installments")["order_id"].count().reset_index().rename(columns={'order_id': 'payments_count'})
payment_val_by_inst_count = filtered_payments[filtered_payments['payment_type'] == "credit_card"].groupby("payment_installments")["payment_value"].mean().round(2).reset_index()
payment_val_by_inst_count = payment_val_by_inst_count.sort_values(by="payment_value", ascending=False)

# dashboard content
st.title("Payments & Shipping Analysis")
st.markdown("""
This section explores customer payment behavior, shipping cost distribution, and how they relate to order value and logistics.  
It sheds light on the usage of payment types, installment trends, and cost efficiency in shipping operations.
<p style='font-style:italic; margin-top:-8px; font-weight:700;'>Note: Use side bar for filters</p>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Number of Payments", f"{filtered_payments['order_id'].nunique():,}")
col2.metric("Number of Payment Modes", f"{filtered_payments['payment_type'].nunique():,}")
col3.metric("Avg No. of Installments in Installment Payments", f"~{filtered_payments[filtered_payments['payment_installments'] > 1]['payment_installments'].mean():,.0f}")

with st.expander("Payment Types/Modes Description"):
    st.markdown("""
- Credit Card: Payment in installments, the pre-selected number of installments is stored in `payment_installments`, with `payment_sequential` describing the total number of installments, in which it was paid in.
- Wallet: Payments done through the digital wallet.
- Voucher: Payments through discount vouchers (also increase `payment_sequential`), and coupons that are given for promotional, and advertising purposes.
- Debit Card: Payments done through Debit Cards.
""")

col1, col2 = st.columns(2)

fig = px.bar(
    payments_by_type,
    x='payment_type',
    y='payments_count',
    color='payment_type',
    title="Number of Payments by Payment Mode",
    text='payments_count',
    labels={'payment_type': 'Payment Mode', 'payments_count': 'Number of Payments'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col1.plotly_chart(fig)

fig = px.pie(
    payments_by_type,
    names='payment_type',
    values='payments_count',
    title='Payment Mode Distribution',
    labels={'payment_type': 'Payment Mode', 'payments_count': 'Number of Payments'},
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}")
col2.plotly_chart(fig)

with st.expander("Payments Distribution by Type/Mode Summary"):
    st.markdown("""Write the summaries & Metrics/KPIs here""")
    
st.divider()
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Installment Count Distribution in Credit Card Payments</h2>
            """, unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 3, 1])
n = col2.slider(
    f"Select the range of Installment Counts to show:",
    min_value=1,
    max_value=no_of_installments['payment_installments'].unique().max(),
    value=(1,no_of_installments['payment_installments'].unique().max()),
)
selected_quantity = col4.selectbox(
    "Quantity to compare by Installment Count:",
    options=["Number of Payments", "Payment Value"],
    index=0
)
if selected_quantity == "Number of Payments":
    fig = px.bar(
        no_of_installments[no_of_installments["payment_installments"].between(n[0], n[1])],
        x="payment_installments",
        y="payments_count",
        color="payments_count",
        title="Number of Installments in Credit-Card Payments",
        text='payments_count',
        labels={'payment_installments': 'Number of Installments', 'payments_count': 'Number of Payments'},
        template="plotly_white",
        color_continuous_scale=px.colors.sequential.Magenta
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)
    with st.expander("Payments Volume by Installment Count Summary"):
        st.markdown("Kpis: certain number of installments have hikes user friendly numbers, we dont offer installments over 24 months, over 12 installments rarely used.")
elif selected_quantity == "Payment Value":
    fig = px.bar(
        payment_val_by_inst_count[payment_val_by_inst_count["payment_installments"].between(n[0], n[1])],
        x="payment_installments",
        y="payment_value",
        color="payment_value",
        title="Payment Value in Credit Card Payments by Installments Count",
        text='payment_value',
        labels={'payment_installments': 'Number of Installments', 'payment_value': 'Mean Payment Value'},
        template="plotly_white",
        color_continuous_scale=px.colors.sequential.Magenta
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)
    with st.expander("Payment Value by Installments Count Summary"):
        st.markdown("""Kpis: certain number of installments have hikes user friendly numbers, don't offer installemtns over 24 months.
                    -  peaks are skewed as there are only 1 order for each 22 & 23 installment count, implying, these peaks are skewed.
                    -  in the first 12 installments, avg paymetn value is similar but increase slightly, as they are preferred, in general.
                    - The 24 installment count has high payment value with significant number of orders suggesting, it is preferred for high payment value.""")

st.divider()

# st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Bar Plot for State-wise Order Distribution</h2>""", unsafe_allow_html=True)
# col1, col2, col3 = st.columns([1, 2, 1])
col1, col2 = st.columns([1, 6])
col1.markdown("""<p style='margin-top:4rem; font-size:1.2rem; font-weight:bold;'>Options:</p>""", unsafe_allow_html=True)
bin_count = col1.slider("Number of bins:", min_value=5, max_value=50, value=35, step=1)
fig = px.histogram(
    filtered_payments,
    x=filtered_payments['payment_value'],
    nbins=bin_count,
    title="Payment Value Distribution",
    template="plotly_white",
    marginal="box",
    opacity=0.6,
    color_discrete_sequence=["#C363FA"],
)
fig.update_layout(
    xaxis_title="Payment Value",
    yaxis_title="Number of Payments",
    bargap=0.05,
    title_x=0.5
)
fig.update_traces(marker_line_width=1, marker_line_color="white")
col2.plotly_chart(fig)

col1, col2 = st.columns([5,3])
fig = px.box(
    filtered_payments,
    x='payment_type',
    y='payment_value',
    points='outliers',
    color='payment_type',
    title="Payment Value Distribution by Payment Mode",
    labels={
        'payment_type': 'Payment Mode',
        'payment_value': 'Payment Value'
    },
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig.update_layout(
    xaxis_title=None,
    yaxis_title="Payment Value",
    xaxis_tickangle=-45,
    font=dict(size=13),
    showlegend=False,
    margin=dict(l=30, r=30, t=20, b=80)
)
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
col1.plotly_chart(fig)

fig = px.bar(
    filtered_payments.groupby("payment_type")["payment_value"].mean().round(2).reset_index().sort_values(by="payment_value", ascending=False),
    x="payment_type",
    y="payment_value",
    color="payment_type",
    title="Avg Payment Value by Payment Mode",
    text='payment_value',
    labels={'payment_type': 'Number of Installments', 'payment_value': 'Mean Payment Value'},
    template="plotly_white"
)
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col2.plotly_chart(fig)

st.divider()

grouped_categories = defaultdict(list)
for category, group in category_map.items():
    grouped_categories[group].append(category)


with st.expander("List of Categories in a Group"):
    for group_name, categories in grouped_categories.items():
        st.markdown(f"**{group_name}**:")
        st.write(categories)

col1, col2 = st.columns([1,6])
col1.markdown("<p style='padding-top:6rem; font-size:1rem;'>Include Toys_Baby Product Group:</p>", unsafe_allow_html=True)
include_toys = col1.radio(
    "",
    options=["Yes", "No"],
    index=1,
    horizontal=False
)
if include_toys == "No":
    fig = px.bar(
        products_by_group.iloc[1:],
        x="product_group_name",
        y="products_count",
        color="product_group_name",
        title="Products Group Distribution [Excluding Toys_Baby]",
        text='products_count',
        labels={'product_group_name': 'Category', 'products_count': 'Number of Products'},
        template="plotly_white"
    )
elif include_toys == "Yes":
    fig = px.bar(
        products_by_group,
        x="product_group_name",
        y="products_count",
        color="product_group_name",
        title="Products Group Distribution [Excluding Toys_Baby]",
        text='products_count',
        labels={'product_group_name': 'Product Group', 'products_count': 'Number of Products'},
        template="plotly_white"
    )
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
col2.plotly_chart(fig)


selected_quantity = st.selectbox(
    "Select Quantity to Explore:",
    options=["price", "shipping price", "delivery time", "weight", "volume"],
    index=1
)

if selected_quantity == "price":
    fig = px.bar(
        products_price_by_group,
        x="product_group_name",
        y="price",
        color="product_group_name",
        title="Products Avg Price Distribution by Group",
        text='price',
        labels={'product_group_name': 'Product Group', 'price': 'Price'},
        template="plotly_white"
    )
elif selected_quantity == "shipping price":
    fig = px.bar(
        shipping_price_by_group,
        x="product_group_name",
        y="shipping_charges",
        color="product_group_name",
        title="Shipping Price Distribution by Group",
        text='shipping_charges',
        labels={'product_group_name': 'Product Group', 'shipping_charges': 'Shipping Price'},
        template="plotly_white"
    )
elif selected_quantity == "delivery time":
    fig = px.bar(
        delivery_time_by_group,
        x="product_group_name",
        y="delivery_time_gap_hrs",
        color="product_group_name",
        title="Delivery Time Distribution by Group",
        text='delivery_time_gap_hrs',
        labels={'product_group_name': 'Product Group', 'delivery_time_gap_hrs': 'Delivery Time (hrs)'},
        template="plotly_white"
    )
elif selected_quantity == "weight":
    fig = px.bar(
        product_weight_by_group,
        x="product_group_name",
        y="product_weight_g",
        color="product_group_name",
        title="Product Weight (g) Distribution by Group",
        text='product_weight_g',
        labels={'product_group_name': 'Product Group', 'product_weight_g': 'Weight (g)'},
        template="plotly_white"
    )
elif selected_quantity == "volume":
    fig = px.bar(
        product_volume_by_group,
        x="product_group_name",
        y="product_volume_cm3",
        color="product_group_name",
        title="Products Volume Distribution by Group",
        text='product_volume_cm3',
        labels={'product_group_name': 'Product Group', 'product_volume_cm3': 'Volume (cm3)'},
        template="plotly_white"
    )
fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig)

if selected_quantity == "price":
    fig = px.box(
        filtered_products,
        x='product_group_name',
        y='price',
        points='outliers',
        color='product_group_name',
        title="Product Price Distribution by Group",
        labels={
            'product_group_name': 'Product Group',
            'price': 'Product Price'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Product Price",
        xaxis_tickangle=-45,
        font=dict(size=13),
        showlegend=False,
        margin=dict(l=30, r=30, t=20, b=80)
    )
elif selected_quantity == "shipping price":
    fig = px.box(
        products_order_items,
        x='product_group_name',
        y='shipping_charges',
        points='outliers',
        color='product_group_name',
        title="Shipping Price Distribution by Group",
        labels={
            'product_group_name': 'Product Group',
            'shipping_charges': 'Shipping Price'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Product Shipping Price",
        xaxis_tickangle=-45,
        font=dict(size=13),
        showlegend=False,
        margin=dict(l=30, r=30, t=20, b=80)
    )
elif selected_quantity == "delivery time":
    fig = px.box(
        products_items_orders,
        x='product_group_name',
        y='delivery_time_gap_hrs',
        points='outliers',
        color='product_group_name',
        title="Delivery Time Distribution By Group",
        labels={
            'product_group_name': 'Product Group',
            'delivery_time_gap_hrs': 'Delivery Time Gap (hrs)'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Delivery Time Gap (hrs)",
        xaxis_tickangle=-45,
        font=dict(size=13),
        showlegend=False,
        margin=dict(l=30, r=30, t=20, b=80)
    )
elif selected_quantity == "weight":
    fig = px.box(
        filtered_products,
        x='product_group_name',
        y='product_weight_g',
        points='outliers',
        color='product_group_name',
        title="Product Weight Distribution by Group",
        labels={
            'product_group_name': 'Product Group',
            'product_weight_g': 'Product Weight (g)'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Product Weight (grams)",
        xaxis_tickangle=-45,
        font=dict(size=13),
        showlegend=False,
        margin=dict(l=30, r=30, t=20, b=80)
    )
elif selected_quantity == "volume":
    fig = px.box(
        filtered_products,
        x='product_group_name',
        y='product_volume_cm3',
        points='outliers',
        color='product_group_name',
        title="Product Volume Distribution By Group",
        labels={
            'product_group_name': 'Product Group',
            'product_volume_cm3': 'Product Volume (cm^3)'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Product Volume (cm^3)",
        xaxis_tickangle=-45,
        font=dict(size=13),
        showlegend=False,
        margin=dict(l=30, r=30, t=20, b=80)
    )
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
st.plotly_chart(fig, use_container_width=True)
