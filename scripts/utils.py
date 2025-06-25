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

def get_state_code_names():
    return {
        "AC": "Acre",
        "AL": "Alagoas",
        "AP": "Amapá",
        "AM": "Amazonas",
        "BA": "Bahia",
        "CE": "Ceará",
        "DF": "Distrito Federal",
        "ES": "Espírito Santo",
        "GO": "Goiás",
        "MA": "Maranhão",
        "MT": "Mato Grosso",
        "MS": "Mato Grosso do Sul",
        "MG": "Minas Gerais",
        "PA": "Pará",
        "PB": "Paraíba",
        "PR": "Paraná",
        "PE": "Pernambuco",
        "PI": "Piauí",
        "RJ": "Rio de Janeiro",
        "RN": "Rio Grande do Norte",
        "RS": "Rio Grande do Sul",
        "RO": "Rondônia",
        "RR": "Roraima",
        "SC": "Santa Catarina",
        "SP": "São Paulo",
        "SE": "Sergipe",
        "TO": "Tocantins"
    }
def get_region_states():
    return {
        "North": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
        "North-East": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
        "Mid-West": ["DF", "GO", "MT", "MS"],
        "South-East": ["ES", "MG", "RJ", "SP"],
        "South": ["PR", "RS", "SC"]
    }