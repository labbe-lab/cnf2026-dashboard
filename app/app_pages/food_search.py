# to see app in streamlit, run the following code in terminal from the cnf2026_database folder
# python -m streamlit run app/app.py

# import libraries
import streamlit as st
from pathlib import Path
from PIL import Image
from cnf_functions import *



# Find project root folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Connect to database
database_path = BASE_DIR / "database" / "CNF2026.db"

conn = get_connection(database_path)


# Enable foreign keys
conn.execute("PRAGMA foreign_keys = ON;")

# Initialize Streamlit session state variables
if "selected_food_code" not in st.session_state:
    st.session_state.selected_food_code = None

if "food_dashboard" not in st.session_state:
    st.session_state.food_dashboard = None

# Load logos for top of food search page
# Import logos
logos = Image.open(BASE_DIR / "logo" / "logos.png")

# Specify location of logos (on top of disclaimer, right side)
left, logo = st.columns([10, 3])

with logo:
    st.image(logos, width=350)


# Add project disclaimer at the top of the page
st.markdown(
    """
    <div style="
        background-color: #e8f4fd;
        padding: 10px 10px 2px 10px;
        border-radius: 4px;
        font-size: 14px;
        line-height: 1.1;
        margin-bottom: 5px;
    ">
    <b>Disclaimer</b><br><br>

    This dashboard was developed as part of an independent academic project and is not
    endorsed by or affiliated with Health Canada.<br>

    It uses the publicly available Canadian Nutrient File (CNF) 2026 data from Health
    Canada and was developed to make finding food nutrient profiles easier. It was modelled
    after the CNF – Search by food tool created for the 2015 CNF.<br>

    This dashboard does not replace the official CNF 2026 resources, which are available from Health Canada:
    <a href="https://www.canada.ca/en/health-canada/services/food-nutrition/healthy-eating/nutrient-data/canadian-nutrient-file-about-us.html">
    Canadian Nutrient File - Health Canada</a>
    </div>
    """,
    unsafe_allow_html=True
)


# Create function to store selected food code and navigate to the food details page
def select_food(food_code):

    # Save selected food code for use across Streamlit pages
    st.session_state.selected_food_code = food_code

    # Clear previous dashboard information
    st.session_state.food_dashboard = None

    # Open food details page
    st.switch_page(
        "app_pages/food_details.py"
    )

# Define helper function to display formatted food search results
# Also allows user to select a single food from the search results
def display_food_results(results):

    if results.empty:
        st.warning("No foods found.")
        return

    search_results_display = food_search_display(results)

    st.write("Click a Food Code to select a food:")

    # Create table header
    header_cols = st.columns([1, 4, 4])

    header_cols[0].write("**Food Code**")
    header_cols[1].write("**Food Description (English)**")
    header_cols[2].write("**Food Description (French)**")


    # Create table rows
    for _, row in search_results_display.iterrows():

        cols = st.columns([1, 4, 4])

        # Food Code button
        if cols[0].button(
            str(row["Food Code"]),
            key=f"food_{row['Food Code']}_{row.name}"
        ):
            select_food(row["Food Code"])

        # Descriptions remain normal text
        cols[1].write(row["Food Description (English)"])
        cols[2].write(row["Food Description (French)"])


# 2026 CNF Dashboard Title
st.title("Canadian Nutrient File (CNF) 2026 Dashboard")

st.write(
    "Search for a food to view nutrient composition information."
)
    
# Food Search - using a search term
search_term = st.text_input(
    "Enter a food name:",
    placeholder="e.g., apple, bread, chicken"
)

# Food Search - using a known CNF food code
food_code_search = st.number_input(
    "Enter CNF Food Code:",
    min_value=1,
    step=1,
    value=None,
    placeholder="e.g., 4066"
)


# If a CNF food code was entered in the search
if food_code_search is not None:

    # Search database using Food_Code
    search_results = search_food_code(
        food_code_search,
        conn
    )

    # Check whether Food_Code exists
    if search_results.empty:

        st.warning(
            f"No food found with Food Code {food_code_search}. Please check the code and try again."
        )

    else:

       st.write("Food found:")

       display_food_results(search_results)


# If no CNF food code is entered but a search term is entered
elif search_term:

    # Search database using food description
    search_results = search_food(
        search_term,
        conn
    )

    # Check whether any foods matched the search
    if search_results.empty:

        st.warning(
            f'No foods found matching "{search_term}". Please try another search term.'
        )

    else:

        st.write(
            f"Found **{len(search_results)}** matching foods."
        )

        # Optional filter
        filter_term = st.text_input(
            "Filter search results (optional):",
            placeholder="e.g., juice, raw, canned"
        )

        # Apply filter if entered
        filtered_results = search_results.copy()

        if filter_term:

            filtered_results = filtered_results[
                filtered_results["Food_Description_EN"].str.contains(
                    filter_term,
                    case=False,
                    na=False
                )
                |
                filtered_results["Food_Description_FR"].str.contains(
                    filter_term,
                    case=False,
                    na=False
                )
            ]

            # Check whether any foods remain after filtering
            if filtered_results.empty:

                st.warning(
                    f'No foods matched after filtering by "{filter_term}". Please try a different filter or clear the filter to see all search results.'
                )

            else:

                st.write(
                    f"Showing **{len(filtered_results)}** matching foods after filtering."
                )

                display_food_results(filtered_results)
      
        else:
            
            display_food_results(search_results)


# Dashboard footer with lab information
st.markdown(
    """
    <hr style="margin-top: 25px; margin-bottom: 13px;">

    <div style="
        font-size: 13px;
        color: #666;
        text-align: center;
    ">
        This dashboard was developed by the <b>L'Abbé Lab</b> at the University of Toronto.
        <br>
        If you have questions, feedback, or comments, please contact:
        <b>labbe.lab@utoronto.ca</b>
    </div>
    """,
    unsafe_allow_html=True
)