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
st.set_page_config(page_title="Payments & Shipping - EDA", page_icon="💳", initial_sidebar_state="expanded", layout='wide')
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
selected_payment_types = st.sidebar.multiselect(
    "Select Payment Modes:",
    options=payments["payment_type"].value_counts().index.tolist(),
    default=payments["payment_type"].value_counts().index.tolist()
)
selected_states = [state for region in selected_regions for state in region_states_dict[region]]

# TODO: see if these filters are needed or not
filtered_orders = orders[orders["order_purchase_timestamp"].dt.year == int(selected_year)] if selected_year != 'All' else orders
filtered_orders = filtered_orders[filtered_orders["order_status"].isin(selected_order_status)]

# TODO: see if i can filter customers based on filtered orders
filtered_customers = customers[customers["customer_id"].isin(filtered_orders["customer_id"])]
filtered_customers = filtered_customers[filtered_customers["customer_state"].isin(selected_states)]

filtered_payments = payments[
    (payments["order_id"].isin(filtered_orders["order_id"])) &
    (payments["payment_type"].isin(selected_payment_types))
]

valid_order_ids = filtered_payments["order_id"].unique()

filtered_orders      = filtered_orders[filtered_orders["order_id"].isin(valid_order_ids)] 
filtered_order_items = order_items[order_items["order_id"].isin(valid_order_ids)]         
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
payments_order_items = payments.merge(filtered_order_items, on="order_id")
payments_orders = payments.merge(filtered_orders, on="order_id")
payments_items_delivery_time = payments_order_items.merge(orders[['order_id', 'order_delivered_timestamp']], on='order_id', how='left')


# for this one:
@st.cache_data
def compute_plotting_dfs():
    payments_by_type = filtered_payments.groupby("payment_type")["order_id"].count().reset_index().rename(columns={'order_id': 'payments_count'})
    payments_by_type = payments_by_type.sort_values(by="payments_count", ascending=False)

    payments_by_month = payments_orders.groupby(filtered_orders['order_delivered_timestamp'].dt.to_period('M'))['payment_value'].sum().reset_index().rename(columns={'order_delivered_timestamp':'month'})
    payments_by_month['month'] = payments_by_month['month'].dt.strftime('%m-%Y')
    shipping_price_by_month = payments_items_delivery_time.groupby(filtered_orders['order_delivered_timestamp'].dt.to_period('M'))['shipping_charges'].sum().reset_index().rename(columns={'order_delivered_timestamp':'month'})
    shipping_price_by_month['month'] = shipping_price_by_month['month'].dt.strftime('%m-%Y')

    no_of_installments = filtered_payments[filtered_payments['payment_type'] == "credit_card"].groupby("payment_installments")["order_id"].count().reset_index().rename(columns={'order_id': 'payments_count'})
    payment_val_by_inst_count = filtered_payments[filtered_payments['payment_type'] == "credit_card"].groupby("payment_installments")["payment_value"].mean().round(2).reset_index()
    payment_val_by_inst_count = payment_val_by_inst_count.sort_values(by="payment_value", ascending=False)

    return (payments_by_type, payments_by_month, shipping_price_by_month, no_of_installments, payment_val_by_inst_count)

(payments_by_type, 
 payments_by_month, 
 shipping_price_by_month, 
 no_of_installments, 
 payment_val_by_inst_count) = compute_plotting_dfs()


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
    st.markdown("""
- Credit Cards dominate with ~74% of all transactions, showing trust in and access to credit-based purchases, possibly aided by installment support.
- Digital Wallets show strong adoption at ~19.3%, indicating a growing preference for quick, convenient, and tech-driven payments.
- Vouchers & Debit Cards are underutilized, together forming just 7%, highlighting potential for better promotion of pre-paid and debit-based options.
""")
    
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
        st.markdown("""
- The Installment Count distribution shows a preference for favorable number of installments such as 2, 3, 6, 8, 12, 15, 18, and 24.
- The most common installment count (other than 1) is less than 12, suggesting that customers prefer lesser number of installments for their orders.
- The odd installment counts like 7, 9, 17 etc are rarely used, indicating that customers prefer even installment counts, and psychological behavior influences this decision.""")
        col1, col2, col3 = st.columns(3)
        col1.metric("Most Common Installment Count", f"{no_of_installments['payment_installments'].mode()[0]}")
        col2.metric("Order Volume for > 12 Installments", f"{no_of_installments[no_of_installments['payment_installments'] > 12]['payments_count'].sum()}")
        col3.metric("Order Volume for Favorable Installment Counts", f"{no_of_installments[no_of_installments['payment_installments'].isin([3,6,8,10,12,15,18, 24])]['payments_count'].sum()} ({no_of_installments[no_of_installments['payment_installments'].isin([3,6,8,10,12,15,18, 24])]['payments_count'].sum() / no_of_installments['payments_count'].sum():.1%})")
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
        st.markdown("""
        - Certain number of installments have hikes user friendly numbers, don't offer installments over 24 months.
        - Peaks are skewed as there are only 1 order for each 22 & 23 installment count, implying, these peaks are skewed.
        - In the first 12 installments, avg payment value is similar but increase slightly, as they are preferred, in general.
        - The 24 installment count has high payment value with significant number of orders suggesting, it is preferred for high payment value.
        """)

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

with st.expander("Payment Value Distribution Summary"):
    st.markdown("""- All the payment modes have a similar distribution, with Credit Cards having the highest payment value, followed by Digital Wallets, Vouchers, and Debit Cards.
- The box plot shows that Credit Cards have a wider range of payment values, with most outliers on the higher end, indicating that customers are willing to spend more when using credit cards.
- While this behavior is not the same in the debit cards & vouchers.
    """)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    col2.metric("Median Payment Value", f"{filtered_payments['payment_value'].median():,.2f}")
    col3.metric("75% of Payment Value Falls Below", f"{filtered_payments['payment_value'].quantile(0.75):,.2f}")

st.divider()
col1, col2 = st.columns([1, 6])
col1.markdown("""<p style='margin-top:4rem; font-size:1.2rem; font-weight:bold;'>Options:</p>""", unsafe_allow_html=True)
bin_count = col1.slider("Select number of bins:", min_value=5, max_value=50, value=35, step=1)
selected_quantity = col1.radio(
    "Choose Quantity to Analyze:",
    options=["Shipping Charges", "Shipping-to-Price Ratio"],
    index=0,
    horizontal=False
)
if selected_quantity == "Shipping Charges":
    fig = px.histogram(
        payments_order_items,
        x="shipping_charges",
        nbins=bin_count,
        title="Shipping Price Distribution",
        template="plotly_white",
        marginal="box",
        opacity=0.6,
        color_discrete_sequence=["#801B52"],
    )
    fig.update_layout(
        xaxis_title="Shipping Charges",
        yaxis_title="Number of Payments",
        bargap=0.05,
        title_x=0.5
    )
    fig.update_traces(marker_line_width=1, marker_line_color="white")
    col2.plotly_chart(fig)
    with st.expander("Shipping Charges Distribution Summary"):
        st.markdown("""- Most of the shipping charges fall below 70, suggesting a majority of orders have low shipping costs, likely due to efficient logistics and regional proximity, but this from previous analysis, is due to the high volume of orders with better logistics."
- The distribution shows a long tail, indicating that while most orders have low shipping costs, there are some with significantly higher charges, possibly due to longer distances or heavier items.""")
        col1, col2, col3 = st.columns(3)
        col1.metric("Median Shipping Charges", f"{payments_order_items['shipping_charges'].median():,.2f}")
        col2.metric("90% of Shipping Charges Falls Below", f"{payments_order_items['shipping_charges'].quantile(0.9):,.2f}")
        col3.metric("Threshold for High Shipping Charges", f"{payments_order_items['shipping_charges'].quantile(0.95):,.2f}")
elif selected_quantity == "Shipping-to-Price Ratio": 
    fig = px.histogram(
        payments_order_items,
        x="shipping_price_ratio",
        nbins=bin_count,
        title="Shipping-to-Price Ratio",
        template="plotly_white",
        marginal="box",
        opacity=0.6,
        color_discrete_sequence=["#47B7B7"],
    )
    fig.update_layout(
        xaxis_title="Shipping-Price Ratio",
        yaxis_title="Number of Payments",
        bargap=0.05,
        title_x=0.5
    )
    fig.update_traces(marker_line_width=1, marker_line_color="white")
    col2.plotly_chart(fig)
    with st.expander("Shipping-Price Ratio Distribution Summary"):
        st.markdown("""
- The Shipping-to-Price Ratio distribution shows that most orders have a ratio below 0.5, indicating that shipping costs are generally low relative to the order value, with room for improvement.
- There exists a long tail in the distribution, suggesting that while most orders have a low shipping-to-price ratio, there are some with significantly higher ratios, possibly due to high-value items or longer shipping distances.""")
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
        col2.metric("75% of Shipping-Price Ratio Falls Below", f"{payments_order_items['shipping_price_ratio'].quantile(0.75):.2f}")
        col3.metric("Order Volume for Shipping-Price Ratio > 0.5", f"{payments_order_items[payments_order_items['shipping_price_ratio'] > 0.5]['order_id'].nunique():,} ({payments_order_items[payments_order_items['shipping_price_ratio'] > 0.5]['order_id'].nunique() / payments_order_items['order_id'].nunique():.1%})")
st.divider()
col1, col2 = st.columns([1, 6])
st.markdown("""<h2 style='font-size:1.5rem; font-weight:700;'>Monthly Trends in Payments & Shipping</h2>""", unsafe_allow_html=True)
col1.markdown("""<p style='margin-top:4rem; font-size:1.2rem; font-weight:bold;'>Options:</p>""", unsafe_allow_html=True)
bin_count = col1.slider("Select number of bins: ooga booga", min_value=5, max_value=50, value=35, step=1)
selected_quantity = col1.radio(
    "Choose Quantity to Analyze:",
    options=["Payments", "Shipping Charges"],
    index=0,
    horizontal=False
)
if selected_quantity == "Payments":
    fig = px.bar(
        payments_by_month,
        x='month',
        y='payment_value',
        color='month',
        title="Monthly Trends in Payment Values",
        text='payment_value',
        labels={'month': 'Month', 'payment_value': 'Total Payment Value (of the month)'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    annotations = [
        dict(
            x='12-2017',
            y=payments_by_month[payments_by_month['month'] == '12-2017']['payment_value'].values[0],
            text='<b>New Year</b>',
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            font=dict(size=16)
        ),
        dict(
            x='02-2018',
            y=payments_by_month[payments_by_month['month'] == '02-2018']['payment_value'].values[0],
            text='<b>Carnival</b>',
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-45,
            font=dict(size=16)
        ),
        dict(
            x='05-2018',
            y=payments_by_month[payments_by_month['month'] == '05-2018']['payment_value'].values[0],
            text='<b>Rainy Season Decline</b>',
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            font=dict(size=16)
        )
    ]
    fig.update_layout(annotations=annotations)

    col2.plotly_chart(fig)
    with st.expander("Total Payment Value Monthly Trends Summary"):
        st.markdown("""
- Payment value spikes in Nov 2017, aligning with Black Friday and holiday season.
- Early 2018 sees sustained high activity, likely due to Carnival and dry season logistics.
- Rainy season shows dip, showing a correlation between weather, logistics, and user spending patterns.""")
        
elif selected_quantity == "Shipping Charges":
    fig = px.bar(
        shipping_price_by_month,
        x='month',
        y='shipping_charges',
        color='month',
        title="Monthly Trends in Shipping Charges",
        text='shipping_charges',
        labels={'month': 'Month', 'shipping_charges': 'Total Shipping Charges (in the month)'},
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    annotations = [
        dict(
            x='12-2017',
            y=shipping_price_by_month[shipping_price_by_month['month'] == '12-2017']['shipping_charges'].values[0],
            text='<b>New Year</b>',
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            font=dict(size=16)
        ),
        dict(
            x='02-2018',
            y=shipping_price_by_month[shipping_price_by_month['month'] == '02-2018']['shipping_charges'].values[0],
            text='<b>Carnival</b>',
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-45,
            font=dict(size=16)
        ),
        dict(
            x='05-2018',
            y=shipping_price_by_month[shipping_price_by_month['month'] == '05-2018']['shipping_charges'].values[0],
            text='<b>Rainy Season Decline</b>',
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            font=dict(size=16)
        )
    ]
    fig.update_layout(annotations=annotations)
    col2.plotly_chart(fig)
    with st.expander("Shipping Charges Monthly Trends Summary"):
        st.markdown("""
- Surge in orders across diverse regions increases shipping distances and urgency, raising total shipping costs.
- Carnival celebrations in logistics-optimized cities like São Paulo and Rio de Janeiro lead to shorter delivery routes and lower shipping costs.
- Shipping prices reflect not just order volume but also geographic concentration and infrastructure efficiency during key events.""")

