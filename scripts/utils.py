import streamlit as st

def expander_styles():
    st.markdown(
    """
    <style>
    div[data-testid="stExpander"] summary p {
        font-size: 1.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
