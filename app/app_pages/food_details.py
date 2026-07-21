import streamlit as st
from pathlib import Path

from cnf_functions import *


# Find project root folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Connect to database
database_path = BASE_DIR / "database" / "CNF2026.db"

conn = get_connection(database_path)


# Load nutrient lookup table
lookup_path = BASE_DIR / "data" / "ez_generated" / "nutrients_categorized_EZ.csv"

nutrient_lookup = load_nutrient_lookup(
    lookup_path
)

##### LOAD SELECTED FOOD ######

# Check that a food was selected
if "selected_food_code" not in st.session_state or st.session_state.selected_food_code is None:

    st.warning(
        "No food selected. Please return to the Food Search page."
    )

    st.stop()


# Retrieve selected food code
food_code = st.session_state.selected_food_code

# Reset the cached food dashboard when a new food is selected
# This ensures that selecting a different food loads the correct:
# - food information
# - nutrient data
# - serving size options
# - refuse information
if (
    "loaded_food_code" not in st.session_state
    or st.session_state.loaded_food_code != food_code
):

    st.session_state.food_dashboard = None

    st.session_state.loaded_food_code = food_code

# Add button to return to search page
return_button = st.button("Return to Food Search")

if return_button:
    st.switch_page(
        "app_pages/food_search.py"
    )

# Reduce spacing between return button and page title
st.markdown(
    """
    <style>
    div[data-testid="stButton"] {
        margin-bottom: -25px;
    }

    h1 {
        margin-top: -20px;
        margin-bottom: -20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Page title
st.title(
    "Nutrient Profile"
)


##### DISPLAY FOOD INFORMATION ######


# Load food information
if st.session_state.food_dashboard is None:

    st.session_state.food_dashboard = load_food_data(
        food_code=food_code,
        conn=conn,
        nutrient_lookup=nutrient_lookup
    )


# Retrieve dashboard components
# The wrapper function returns a dictionary containing:
# (1) food information
# (2) nutrient information per 100 g
# (3) available serving size conversions
# (4) refuse for the selected food (if available)
food_data = st.session_state.food_dashboard

nutrients = food_data["nutrients"]

serving_options = food_data["serving_options"]

refuse = food_data["refuse"]

# Display food information

food_info = food_data["food_info"].iloc[0]

st.markdown(
    f"""
    <div style="font-size: 26px; font-weight: 600; margin-bottom: 10px;">
        {food_info["Food Name (English)"]}
    </div>

    <div style="font-size: 21px; font-weight: 400; margin-bottom: 10px;">
        {food_info["Food Name (French)"]}
    </div>

    <div style="font-size: 26px; font-weight: 600; margin-bottom: 10px;">
        Food Code: {food_info["Food Code"]}
    </div>

    <div style="font-size: 13px; color: #666; margin-top: 8px; margin-bottom: 15px;">
        Source: {food_info["Food Source Description"]}
    </div>
    """,
    unsafe_allow_html=True
)


###### DISPLAY % REFUSE ######


# Display percent refuse if available
# If no refuse information exists for the selected food, this section will not be displayed
if not refuse.empty and pd.notna(refuse["% Refuse"].iloc[0]):

    refuse_value = refuse["% Refuse"].iloc[0]

    st.markdown(
        f"**% Refuse: {refuse_value:.0f}%**",
        help=(
            "Refuse refers to the parts of food that are not eaten, "
            "such as seeds, bones, and skin."
        )
    )


##### CHOOSE SERVING SIZE ######


# Add serving size dropdown
# The default CNF option (per 100 g of edible portion) remains available
# Users can select an alternate serving size to convert nutrient values
# Adjust dropdown label size
st.markdown(
    """
    <style>
    label[data-testid="stWidgetLabel"] {
        font-size: 18px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

selected_serving = st.selectbox(
    "Choose a serving size:",
    serving_options["Serving Display"]
)

# Retrieve the selected serving size information
# This identifies the selected serving option and extracts:
# - Weight (g): used to convert nutrient values from per 100 g
# - Serving Size: original serving description used for nutrient column names
#
# Example:
#     Serving Display = "1 slice = 36.5 g"
#     Serving Size = "1 slice"
#     Weight (g) = 36.5

selected_row = serving_options[
    serving_options["Serving Display"] == selected_serving
].iloc[0]


selected_weight = selected_row["Weight (g)"]

selected_label = selected_row["Serving Size"]

# Convert nutrients to the selected serving size
# Nutrient values are originally provided per 100 g
# If the user selects per 100 g, no conversion is required

if selected_serving == "Per 100 g of edible portion":

    converted_nutrients = round_nutrient_values(
        nutrients
    )

else:

    converted_nutrients = calculate_nutrients_per_serving(
        nutrient_data=nutrients,
        serving_weight=selected_weight,
        serving_label=selected_label
    )


##### SEARCH NUTRIENTS ######


# Add nutrient search box
# Allows the user to filter nutrients by name (e.g., "protein", "vitamin")
# The search is case-insensitive and searches only the nutrient names

nutrient_search = st.text_input(
    "Filter for a nutrient",
    placeholder="Example: protein, sodium, vitamin C"
)

# Filter nutrient table if the user entered a search term
if nutrient_search:

    converted_nutrients = converted_nutrients[
        converted_nutrients["Nutrient"]
        .str.contains(
            nutrient_search,
            case=False,
            na=False
        )
    ]

# Add small spacing before nutrient composition section
st.markdown(
    "<div style='margin-bottom: 10px;'></div>",
    unsafe_allow_html=True
)


##### FORMAT NUTRIENT TABLES ######

# Display nutrient composition
# If no nutrients match the search term, display a message
# Otherwise display one table for each nutrient category
st.subheader(
    "Nutrient Composition"
)

# Reduce spacing before nutrient category headers
st.markdown(
    "<div style='margin-bottom: -10px;'></div>",
    unsafe_allow_html=True
)

# Create nutrient tables after filtering
converted_tables = format_nutrient_display(
    converted_nutrients
)

if converted_nutrients.empty:

    st.info(
        "No nutrients matched your search."
    )

else:
    
    for category, table in converted_tables.items():

        # Display nutrient category headings with smaller font size
        st.markdown(
            f"""
            <div style="
                font-size: 20px;
                font-weight: 600;
                margin-top: 5px;
                margin-bottom: 8px;
            ">
                {category}
            </div>
            """,
            unsafe_allow_html=True
        )

        formatted_table = apply_nutrient_formatting(
            table
        )

        st.dataframe(
            formatted_table,
            hide_index=True,
            use_container_width=True
        )