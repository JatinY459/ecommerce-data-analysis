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

def get_category_map():
    return {
        # 🎮 Toys & Baby Combined
        'toys': 'toys_baby',
        'baby': 'toys_baby',

        # 🎁 Miscellaneous / Unclassified Fun Stuff
        'cool_stuff': 'miscellaneous',
        'flowers': 'miscellaneous',
        'market_place': 'miscellaneous',
        'party_supplies': 'miscellaneous',
        'christmas_supplies': 'miscellaneous',

        # 🔧 Construction / Tools
        'costruction_tools_garden': 'Construction/Tools',
        'construction_tools_construction': 'Construction/Tools',
        'construction_tools_lights': 'Construction/Tools',
        'construction_tools_safety': 'Construction/Tools',
        'costruction_tools_tools': 'Construction/Tools',
        'garden_tools': 'Construction/Tools',
        'home_construction': 'Construction/Tools',
        'signaling_and_security': 'Construction/Tools',

        # 🛋️ Furniture
        'furniture_decor': 'Furniture',
        'furniture_living_room': 'Furniture',
        'office_furniture': 'Furniture',
        'furniture_bedroom': 'Furniture',
        'furniture_mattress_and_upholstery': 'Furniture',
        'kitchen_dining_laundry_garden_furniture': 'Furniture',

        # 🏠 Home Appliances
        'home_appliances': 'Home Appliances',
        'home_appliances_2': 'Home Appliances',
        'small_appliances': 'Home Appliances',
        'small_appliances_home_oven_and_coffee': 'Home Appliances',
        'home_comfort_2': 'Home Appliances',
        'home_confort': 'Home Appliances',

        # 💄 Beauty & Health
        'health_beauty': 'Beauty & Health',
        'perfumery': 'Beauty & Health',

        # 👗 Fashion
        'fashion_shoes': 'Fashion',
        'fashion_male_clothing': 'Fashion',
        'fashion_female_clothing': 'Fashion',
        'fashion_childrens_clothes': 'Fashion',
        'fashion_sport': 'Fashion',
        'fashion_underwear_beach': 'Fashion',
        'fashion_bags_accessories': 'Fashion',
        'luggage_accessories': 'Fashion',

        # ⚽ Sports
        'sports_leisure': 'Sports',

        # 🏠 House & Living
        'bed_bath_table': 'House & Living',
        'housewares': 'House & Living',
        'la_cuisine': 'House & Living',

        # 📚 Books
        'books_technical': 'Books',
        'books_general_interest': 'Books',
        'books_imported': 'Books',

        # 🎨 Arts & Creativity
        'art': 'Arts & Creativity',
        'arts_and_craftmanship': 'Arts & Creativity',
        'stationery': 'Arts & Creativity',

        # 💻 Electronics
        'electronics': 'Electronics',
        'computers': 'Electronics',
        'computers_accessories': 'Electronics',
        'tablets_printing_image': 'Electronics',
        'audio': 'Electronics',
        'telephony': 'Electronics',
        'fixed_telephony': 'Electronics',
        'cine_photo': 'Electronics',
        'consoles_games': 'Electronics',
        'air_conditioning': 'Electronics',

        # 🍔 Food & Drinks
        'food': 'Food & Drinks',
        'food_drink': 'Food & Drinks',
        'drinks': 'Food & Drinks',

        # 🐶 Pet
        'pet_shop': 'Pet',

        # 🚗 Auto
        'auto': 'Auto',

        # 🏭 Industry / Business
        'industry_commerce_and_business': 'Industry & Business',
        'agro_industry_and_commerce': 'Industry & Business',

        # 🎶 Entertainment
        'music': 'Arts & Creativity',
        'dvds_blu_ray': 'Arts & Creativity'
    }
