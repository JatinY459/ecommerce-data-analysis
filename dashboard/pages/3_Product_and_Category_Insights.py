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

st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Categories Distribution by Order Volume & Unique Products</h2>
            Options:""", unsafe_allow_html=True)
selected_quantity = st.selectbox(
    "Select quantity to show:",
    options=["Unique Products", "Order Volume"],
    index=0
    )
col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
orders_by_products = products_items_orders.groupby("product_category_name")["order_id"].count().reset_index().rename(columns={'order_id':'order_counts'})
orders_by_products = orders_by_products.sort_values(by="order_counts", ascending=False)
category_view = col2.radio(
    "View Categories by:",
    options=["Top N", "Bottom N"],
    index=0,
    horizontal=True
)
n = col3.slider(
    f"Select number of categories to show:",
    min_value=1,
    max_value=min(35, 69),
    value=15
)
if category_view == "Top N":
    if selected_quantity == "Order Volume":
            fig = px.bar(
            orders_by_products.iloc[1:n+1],
            x="product_category_name",
            y="order_counts",
            color="product_category_name",
            title=f"Products Order Count by Categories (Top {n}) [Excluding Toys]",
            text='order_counts',
            labels={'product_category_name': 'Product Group', 'order_counts': 'Number of Orders'},
            template="plotly_white"
        )
    elif selected_quantity == "Unique Products":
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
elif category_view == "Bottom N":
    if selected_quantity == "Order Volume":
        fig = px.bar(
            orders_by_products.iloc[-n:-1],
            x="product_category_name",
            y="order_count",
            color="product_category_name",
            title=f"Products Order Count by Categories (Bottom {n})",
            text='order_count',
            labels={'product_category_name': 'Category', 'order_count': 'Number of Orders'},
            template="plotly_white"
        )
    elif selected_quantity == "Unique Products":
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
if selected_quantity == "Order Volume":
    with st.expander("Category Order Volume Summary"):
        st.markdown("Show Number of Orders for Toys & compare toys % to others")
elif selected_quantity == "Unique Products":
    with st.expander("Top Product Categories Distribution Summary"):
        st.markdown("""Write the summaries & Metrics/KPIs here""")
        col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 3, 1])
        col2.metric("Mean number of Products (filtered view)", f"{products_by_category.iloc[1:n+1]["products_count"].mean() if category_view=="Top N" else products_by_category.iloc[-n:-1]["products_count"].mean():.2f}")
        col3.metric("Categories with < 10 Products", len(products_by_category[products_by_category['products_count'] < 10]))
        col4.metric("Categories with > 100 Products", f"{len(products_by_category[products_by_category['products_count'] > 100])}")

st.divider()
# st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Bar Plot for State-wise Order Distribution</h2>""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
category_view = col2.radio(
    "Select categories to view",
    options=["Top N", "Bottom N"],
    index=0,
    horizontal=True
)
n = col3.slider(
    f"Select number of categories to view",
    min_value=1,
    max_value=min(35, 69),
    value=15
)
if category_view == "Top N":
    fig = px.bar(
        products_price_by_category.head(n),
        x="product_category_name",
        y="price",
        color="product_category_name",
        title=f"Category Price Distribution Top {n}",
        text='price',
        labels={'product_category_name': 'Category', 'price': 'Price'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

if category_view == "Bottom N":
    fig = px.bar(
        products_price_by_category.tail(n),
        x="product_category_name",
        y="price",
        color="product_category_name",
        title=f"Category Price Distribution Bottom {n}",
        text='price',
        labels={'product_category_name': 'Category', 'price': 'Price'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

# fig = px.bar(
#     products_price_by_category.tail(10),
#     x="product_category_name",
#     y="price",
#     color="product_category_name",
#     title="Category Price Distribution Bottom Half",
#     text='price',
#     labels={'product_category_name': 'Category', 'price': 'Price'},
#     template="plotly_white"
# )
# fig.update_traces(textposition='outside')
# fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
# col2.plotly_chart(fig)

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
