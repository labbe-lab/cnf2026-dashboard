"""
cnf_functions.py

Backend functions used by the 2026 Canadian Nutrient File (CNF) dashboard.

This module contains reusable functions for:

- searching foods using keywords (e.g., apple)
- searching foods using the CNF food_code
- retrieving food information
- retrieving nutrient composition data
- retrieving serving size options
- formatting nutrient tables for display
- loading all dashboard data for a selected food
- converting nutrient values from per 100 g to a selected serving size
"""

# import libraries
import pandas as pd
import sqlite3
import streamlit as st

# 1. Create get_connection function
# To help python files connect to the 2026 CNF database
# Cache-ing will store the connection so Streamlit doesnt have to re-connect everytime it reloads
@st.cache_resource
def get_connection(database_path):

    return sqlite3.connect(
        database_path,
        check_same_thread=False
    )

# 2. Create load_nutrient_lookup() function
# Load and cache the nutrient lookup table
# Cache-ing will store the data so Streamlit doesnt have to re-connect everytime it reloads
@st.cache_data
def load_nutrient_lookup(lookup_path):

    return pd.read_csv(lookup_path)


# 3. Create round_nutrient_values() function
# Applies nutrient-specific rounding rules
# Default = 2 decimal places unless specified otherwise

def round_nutrient_values(nutrient_data):

    # Create copy so original dataframe is preserved
    rounded_data = nutrient_data.copy()


    # Identify nutrient value columns only
    # Includes:
    # - Value per 100 g of edible portion
    # - Value per selected serving size

    value_columns = [
        column for column in rounded_data.columns
        if column.startswith("Value per")
    ]


    # Ensure numeric nutrient columns
    for column in value_columns:

        rounded_data[column] = (
            pd.to_numeric(
                rounded_data[column],
                errors="coerce"
            )
        )

    # ----------------------------------
    # 0 decimal place nutrients
    # ----------------------------------

    zero_decimal_nutrients = [

        "Energy (kcal)",
        "Energy (kJ)",

        "Calcium, Ca",
        "Magnesium, Mg",
        "Phosphorus, P",
        "Potassium, K",
        "Sodium, Na",

        "Beta carotene",
        "Alpha carotene",

        "Retinol",
        "Retinol activity equivalents, RAE",

        "Folacin, total",
        "Folic acid, synthetic form",
        "Folate, naturally occuring",
        "Dietary folate equivalents, DFE",

        "Vitamin D (IU)",

        "Aspartame",
        "Biotin",
        "Caffeine",
        "Theobromine",

        "Lutein and zeaxanthin",
        "Lycopene",

        "Cholesterol"
    ]


    # ----------------------------------
    # 1 decimal place nutrients
    # ----------------------------------

    one_decimal_nutrients = [

        "Fibre, total dietary",

        "Selenium, Se",

        "Choline, total",

        "Vitamin C",

        "Vitamin D",
        "Vitamin D2",
        "Vitamin D3",

        "Vitamin K (menaquinone-4)",
        "Vitamin K (dihydrophylloquinone)",
        "Vitamin K (phylloquinone)"
    ]


    # ----------------------------------
    # 3 decimal place nutrients
    # ----------------------------------

    three_decimal_nutrients = [

        "Copper, Cu",

        "Niacin (nicotinic acid) preformed",
        "Niacin equivalents, total",

        "Riboflavin",
        "Thiamine",
        "Vitamin B-6",

        "Tryptophan",
        "Threonine",
        "Isoleucine",
        "Leucine",
        "Lysine",
        "Methionine",
        "Cystine",
        "Phenylalanine",
        "Tyrosine",
        "Valine",
        "Arginine",
        "Histidine",

        "Alanine",
        "Aspartic acid",
        "Glutamic acid",
        "Glycine",
        "Proline",
        "Serine",
        "Hydroxyproline",

        # Fatty acids
        "Fatty acids, saturated, total",
        "Fatty acids, monounsaturated, total",
        "Fatty acids, polyunsaturated, total",
        "Fatty acids, trans, total",
        "Fatty acids, total trans-monoenoic",
        "Fatty acids, total trans-polyenoic",

        # Plant sterols
        "Total plant sterol",
        "Beta-sitosterol",
        "Campesterol",
        "Stigmasterol"
    ]


    # Add all detailed fatty acid names
    # (kept together so the function is easier to maintain)

    fatty_acid_nutrients = [

        "4:0 (butanoic)",
        "6:0 (hexanoic)",
        "8:0 (octanoic)",
        "10:0 (decanoic)",
        "12:0 (dodecanoic)",
        "13:0 (tridecanoic)",
        "14:0 (tetradecanoic)",
        "15:0 (pentadecanoic",
        "16:0 (heptadecanoic)",
        "17:0 (eicosanoic)",
        "18:0 (octadecanoic)",
        "20:0 (eicosanoic)",
        "22:0 (docosanoic)",
        "24:0 (tetracosanoic)",

        "12:1 (lauroleic)",
        "14:1 (tetradecenoic)",
        "15:1 (pentadecenoic)",
        "16:1 (undifferentiated, hexadecenoic)",
        "16:1c (hexadecenoic)",
        "16:1t (hexadecenoic)",
        "17:1 (heptadecenoic)",

        "18:1 10c",
        "18:1 10t",
        "18:1 11c",
        "18:1 11t",
        "18:1 12c",
        "18:1 12t",
        "18:1 13c",
        "18:1 13t + 14t + 6c-8c",
        "18:1 14c",
        "18:1 15c",
        "18:1 16c",
        "18:1 16t",
        "18:1 4t",
        "18:1 5t",
        "18 1 6t-8t",
        "18:1c (octadecenoic)",
        "18:1t (octadecenoic)",
        "18:1 (undifferentiated, octadecenoic)",

        "20:1 5c",
        "20:1 (eicosenoic)",
        "22:1c (docosenoic)",
        "22:1t (docosenoic)",
        "22:1 (undifferentiated, docosenoic)",
        "24:1c (tetracosenoic)",
        "24:1 (undifferentiated, tetracosenoic)",

        "18:2 9c,13c",
        "18:2 9c,14c",
        "18:2 9c,15c",
        "18:2 c,c n-6 (linoleic, octadecadienoic)",
        "18:2i (linoleic, octadecadienoic)",
        "18:2t (not further defined, linoleic, octadecadienoic)",
        "18:2t,t (octadecadienenoic)",
        "18:2 (undifferentiated, linoleic, octadecadienoic)",
        "18:2 (cla, linoleic, octadecadienoic)",

        "18:3 (c,c,c n-3  linolenic, octadecatrienoic)",
        "18:3 (c,c,c n-6, g-linolenic, octadecatrienoic)",
        "18:3i (linolenic, octadecatrienoic)",
        "18:3 (undifferentiated, linolenic, octadecatrienoic)",
        "18:4 (octadecatetraenoic)",

        "20:2 (c,c  eicosadienoic)",
        "20:3 (n-3 eicosatrienoic)",
        "20:3 (n-6, eicosatrienoic)",
        "20:3 (eicosatrienoic)",
        "20:4 (n-6, arachidonic)",
        "20:4 (eicosatetraenoic)",
        "20:5 (n-3, eicosapentaenoic (EPA))",
        "21:05",
        "22:2 (docosadienoic)",
        "22:03",
        "22:4 (n-6, docosatetraenoic)",
        "22:5 (n-3, docosapentaenoic (DPA))",
        "22:5 (n-6)",
        "22:6 (n-3, docosahexaenoic (DHA))"
    ]

    three_decimal_nutrients.extend(fatty_acid_nutrients)


    # Apply nutrient-specific rounding

    rounding_rules = [
        (zero_decimal_nutrients, 0),
        (one_decimal_nutrients, 1),
        (three_decimal_nutrients, 3)
    ]


    for nutrient_list, decimals in rounding_rules:

        mask = rounded_data["Nutrient"].isin(nutrient_list)

        for column in value_columns:

            rounded_data.loc[mask, column] = (
                rounded_data.loc[mask, column]
                .round(decimals)
            )


    # Save decimal formatting metadata
    decimal_places = {}

    for nutrient in zero_decimal_nutrients:
        decimal_places[nutrient] = 0

    for nutrient in one_decimal_nutrients:
        decimal_places[nutrient] = 1

    for nutrient in three_decimal_nutrients:
        decimal_places[nutrient] = 3


    # Everything not listed remains at default 2 decimals
    rounded_data["Decimal Places"] = (
        rounded_data["Nutrient"]
        .map(decimal_places)
        .fillna(2)
        .astype(int)
    )

    return rounded_data


# 4. Create apply_nutrient_formatting() function
# Apply nutrient-specific decimal formatting for display
def apply_nutrient_formatting(df):

    formatted_df = df.copy()

    # Allow formatted strings in numeric columns
    formatted_df = formatted_df.astype(object)

    value_columns = [
        column for column in formatted_df.columns
        if "Value per" in column
    ]

    for index, row in formatted_df.iterrows():

        decimals = row.get("Decimal Places", 2)

        for column in value_columns:

            value = row[column]

            if pd.notna(value):

                formatted_df.at[index, column] = (
                    f"{float(value):.{int(decimals)}f}"
                )

            else:

                formatted_df.at[index, column] = ""


    # Format number of observations as integers
    if "Number of Observations" in formatted_df.columns:

        formatted_df["Number of Observations"] = (
            pd.to_numeric(
                formatted_df["Number of Observations"],
                errors="coerce"
            )
            .fillna("")
            .apply(
                lambda x: str(int(x))
                if x != ""
                else ""
            )
        )

    if "Standard Error per 100 g" in formatted_df.columns:

        formatted_df["Standard Error per 100 g"] = (
            formatted_df["Standard Error per 100 g"]
            .apply(
                lambda x: f"{x:.2f}"
                if pd.notna(x)
                else ""
            )
        )

    # Remove helper columns before display
    formatted_df = formatted_df.drop(
        columns=[
            "Decimal Places",
            "Nutrient_Category_EZ"
        ],
        errors="ignore"
    )

    # Rename columns for dashboard display
    # Shortens column names while keeping the meaning clear
    formatted_df = formatted_df.rename(
        columns={
            "Number of Observations": "No. of Observations",
            "Standard Error per 100 g": "SE per 100 g"
        }
    )

    return formatted_df


# 5. Create search_food() function
# User enters a search term (e.g., "apple")
# Returns food codes and desciptions that match the search
def search_food(search_term, conn):
    
    query = """
    SELECT DISTINCT
        Food_Code,
        Food_Description_EN,
        Food_Description_FR,
        Alternate_Description_EN,
        Alternate_Description_FR

FROM Food_Name

WHERE Food_Description_EN LIKE ?
    OR Alternate_Description_EN LIKE ?
    OR Food_Description_FR LIKE ?
    OR Alternate_Description_FR LIKE ?

ORDER BY Food_Description_EN;
"""

    search_results = pd.read_sql(
        query,
        conn,
        params=[
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%"
        ]
    )

    return search_results


# 6. Create search_food_code() function
# User enters a search for a CNF food code (e.g., "4066")
# Returns food codes that match that CNF food code
def search_food_code(food_code, conn):

    query = """
    SELECT
        Food_Code,
        Food_Description_EN,
        Food_Description_FR

    FROM Food_Name

    WHERE Food_Code = ?;
    """

    food_results = pd.read_sql(
        query,
        conn,
        params=[food_code]
    )

    return food_results


# 7. Create food_search_display() function
# To simplify the results of the food_search() seen by the user
# Specifically they will only see the Food_Code, Food_Description_EN and Food_Description_FR columns
def food_search_display(search_results):

    food_search_display = search_results[
        [
            "Food_Code",
            "Food_Description_EN",
            "Food_Description_FR"
        ]
    ].copy()

    # Rename columns for dashboard display
    food_search_display = food_search_display.rename(
        columns={
            "Food_Code": "Food Code",
            "Food_Description_EN": "Food Description (English)",
            "Food_Description_FR": "Food Description (French)"
        }
    )

    return food_search_display


# 8. Create get_food_info() function
# Once user has selected a specific food from the list, this will populate the header information for that food
def get_food_info(food_code, conn):
    
    query = """
    SELECT
        Food_Name.Food_Code AS "Food Code",
        Food_Name.Food_Description_EN AS "Food Name (English)",
        Food_Name.Food_Description_FR AS "Food Name (French)",
        Food_Source.Food_Source_Description_EN AS "Food Source Description"

    FROM Food_Name

    JOIN Food_Source
        ON Food_Name.Food_Source_Code = Food_Source.Food_Source_Code

    WHERE Food_Name.Food_Code = ?;
    """

    food_info = pd.read_sql(
        query,
        conn,
        params=[food_code]
    )

    return food_info


# 9. Create get_nutrients() function
# Retrieve nutrient values, add the user-friendly nutrient names and nutrient categories, and order nutrients
def get_nutrients(food_code, conn, nutrient_lookup):

    query = """
    SELECT
        Nutrient_Name.Nutrient_Code,

        Nutrient_Name.Nutrient_Name_EN AS "Nutrient",

        Nutrient_Amount.Nutrient_Amount AS "Value per 100 g of edible portion",

        Nutrient_Name.Nutrient_Unit AS "Unit",

        Nutrient_Amount.Observations AS "Number of Observations",

        Nutrient_Amount.STD_Error AS "Standard Error per 100 g",

        Nutrient_Source.Nutrient_Source_Description_EN AS "Data Source"

    FROM Food_Name

    JOIN Nutrient_Amount
        ON Food_Name.Food_Code = Nutrient_Amount.Food_Code

    JOIN Nutrient_Name
        ON Nutrient_Amount.Nutrient_Code = Nutrient_Name.Nutrient_Code

    JOIN Nutrient_Source
        ON Nutrient_Amount.Nutrient_Source_Code = Nutrient_Source.Nutrient_Source_Code

    WHERE Food_Name.Food_Code = ?

    ORDER BY Nutrient_Name.Nutrient_Code;
    """

    nutrient_data = pd.read_sql(
        query,
        conn,
        params=[food_code]
    )

    nutrient_data["Number of Observations"] = (
        pd.to_numeric(
            nutrient_data["Number of Observations"],
            errors="coerce"
        )
    )

    # Add EZ nutrient categories , order, and user-friendly display names (all based on 2015 web application)
    nutrient_data = nutrient_data.merge(
        nutrient_lookup[
            [
                "Nutrient_Code",
                "Nutrient_Order_EZ",
                "Nutrient_Category_EZ",
                "Nutrient_Name_EN_EZ"
            ]
        ],
        on="Nutrient_Code",
        how="left"
    )

    # Replace CNF nutrient names with EZ user-friendly names
    nutrient_data["Nutrient"] = (
        nutrient_data["Nutrient_Name_EN_EZ"]
    )

    # Sort nutrients according to the manually created display order
    nutrient_data = nutrient_data.sort_values("Nutrient_Order_EZ")
    
    # Reset the dataframe index after sorting so each nutrient category table starts at row 0
    nutrient_data  = nutrient_data.reset_index(drop=True)

    # Keep only dashboard columns
    nutrient_data = nutrient_data[
        [
            "Nutrient_Category_EZ",
            "Nutrient",
            "Unit",
            "Value per 100 g of edible portion",
            "Number of Observations",
            "Standard Error per 100 g",
            "Data Source"
        ]
    ]

    return nutrient_data


# 10. Create a get_serving_options() function
# This will create a list of serving size options available for the user to pick from
# Each serving option includes:
# - The serving description (e.g., "1 slice")
# - The equivalent weight in grams (e.g., 36.5 g)
# - A formatted display label for the dropdown (e.g., "1 slice = 36.5 g")

def get_serving_options(food_code, conn):
    
    query = """
    SELECT
        Measure_Name.Measure_Description_and_Unit_EN AS "Serving Size",
        Measure_Weight_Conversion.Measure_Weight_Conversion AS "Weight (g)"

    FROM Measure_Weight_Conversion

    JOIN Measure_Name 
        ON Measure_Weight_Conversion.Measure_Code = Measure_Name.Measure_Code

    JOIN Measure_Type 
        ON Measure_Weight_Conversion.Measure_Type_Code = Measure_Type.Measure_Type_Code

    WHERE Measure_Weight_Conversion.Food_Code = ?

    AND Measure_Type.Measure_Type_Code != 3;
    """


    # Retrieve serving size conversions from CNF database
    serving_options = pd.read_sql(
        query,
        conn,
        params=[food_code]
    )


    # Add the standard CNF default option
    # This option represents the original nutrient values per 100 g
    # and is not included in the serving conversion table

    default_serving = pd.DataFrame({

        "Serving Size": [
            "Per 100 g of edible portion"
        ],

        "Weight (g)": [
            100
        ]
    })


    # Combine the default per 100 g option with available serving conversions

    serving_options = pd.concat(
        [
            default_serving,
            serving_options
        ],
        ignore_index=True
    )


    # Create serving size labels for dropdown display
    # Keeps the original serving description but adds the equivalent gram weight
    #
    # Examples:
    #     Per 100 g of edible portion
    #     1 slice = 36.5 g
    #     250 mL = 240 g

    serving_options["Serving Display"] = (

        serving_options.apply(

            lambda row:

            row["Serving Size"]

            if row["Serving Size"] == "Per 100 g of edible portion"

            else (
                f'{row["Serving Size"]} = '
                f'{row["Weight (g)"]:.1f}'.rstrip("0").rstrip(".")
                + " g"
            ),

            axis=1
        )
    )


    return serving_options


# 11. Create a get_food_refuse() function
# Retrieves the percent refuse value for the selected food
# Refuse refers to the parts of food that are not eaten
# (e.g., seeds, bones, skin)
#
# In the CNF database:
# Measure_Type_Code = 3 identifies refuse values

def get_food_refuse(food_code, conn):

    query = """
    SELECT
        Measure_Weight_Conversion AS "% Refuse"

    FROM Measure_Weight_Conversion

    WHERE Food_Code = ?

    AND Measure_Type_Code = 3;
    """

    refuse_data = pd.read_sql(
        query,
        conn,
        params=[food_code]
    )

    return refuse_data


# 12. Create calculate_nutrients_per_serving() function
# Converts nutrient information to the serving size selected by the user
def calculate_nutrients_per_serving(
    nutrient_data,
    serving_weight,
    serving_label
):

    serving_data = nutrient_data.copy()

    serving_column = f"★ Value per {serving_label}"

    serving_data[serving_column] = (
        serving_data["Value per 100 g of edible portion"]
        * serving_weight
        / 100
    )

    serving_data = round_nutrient_values(
        serving_data
    )

    serving_data = serving_data[
        [
            "Nutrient_Category_EZ",
            "Nutrient",
            "Unit",
            serving_column,
            "Value per 100 g of edible portion",
            "Number of Observations",
            "Standard Error per 100 g",
            "Data Source",
            "Decimal Places"
        ]
    ]

    return serving_data


# 13. Create format_nutrient_display() function to alter the way the nutrients are displayed
# Will create one data frame per level of Nutrient_Category_EZ and not display the category in the final data
# Function to format nutrient dataframe into separate tables by nutrient category
# The nutrient category becomes the table heading rather than a displayed column
def format_nutrient_display(nutrient_data):

    categories = (
        nutrient_data["Nutrient_Category_EZ"]
        .dropna()
        .unique()
    )

    tables = {}

    for category in categories:

        table = nutrient_data[
            nutrient_data["Nutrient_Category_EZ"] == category
        ].copy()

        tables[category] = table

    return tables


# 14. Create wrapper function load_food_data()
# This will combine functions used in the dashboard AFTER a user select a specific food
## Note: search_food() is not included because it will happen before this wrapper function is used
#
# This wrapper function combines the following functions:
# (1) get_food_info() 
# (2) get_nutrients()
# (3) get_serving_options()
# (4) get_food_refuse()
# (5) format_nutrient_display()
# It loads the default nutrient information per 100 g and all available serving size options
#
# Note: calculate_nutrients_per_serving() is not included because it will be used after this wrapper function,
# once the user selects a serving size they want to see. 
#
# function parameters:
    # food_code -> int, contains the Food_Code selected by the user
    # conn -> connects to the CNF SQLite database
    # nutrient_lookup -> manually created lookup table (contains: Nutrient_Order_EZ, Nutrient_Category_EZ and Nutrient_Name_EZ)
#
# this function will return a dictionary containing a lookup table with:
    # food_info -> food description and source information
    # nutrients -> nutrient composition table per 100 g
    # serving_options -> available serving size conversions
    # dashboard_tables -> nutrient tables separated by nutrient category

def load_food_data(food_code, conn, nutrient_lookup):

    # Retrieve basic food information to display in dashboard header (food code, food description, food source)
    food_info = get_food_info(
        food_code,
        conn
    )

    # Retrieve nutrient composition data for selected food (nutrient values per 100 g, user-friendly nutrient names, nutrient categories, nutrient display order)
    nutrient_info = get_nutrients(
        food_code,
        conn,
        nutrient_lookup
    )

    # Retrieve available serving size options for selected food (serving description (e.g., 1 slice, 1 cup), equivalent weight in grams)
    serving_options = get_serving_options(
        food_code,
        conn
    )

    # Retrieve percent refuse information
    refuse = get_food_refuse(
        food_code,
        conn
    )

    # Convert the nutrient dataframe into separate tables by nutrient category (e.g.,Proximates, Minerals, Vitamins)
    # The nutrient category becomes the table heading rather than a displayed column
    dashboard_tables = format_nutrient_display(
        nutrient_info
    )

    # Return all components as a dictionary
    # This allows the dashboard to access each component separately
    return {
        "food_info": food_info,
        "nutrients": nutrient_info,
        "serving_options": serving_options,
        "dashboard_tables": dashboard_tables,
        "refuse": refuse
    }

