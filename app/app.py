import streamlit as st
from pathlib import Path

st.set_page_config(
    layout="wide"
)

APP_DIR = Path(__file__).parent

pages = [
    st.Page(
        APP_DIR / "app_pages" / "food_search.py",
        title="Food Search"
    ),
    st.Page(
        APP_DIR / "app_pages" / "food_details.py",
        title="Nutrient Profile"
    )
]

pg = st.navigation(pages)

pg.run()