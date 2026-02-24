import streamlit as st
import pandas as pd
import re
import numpy as np

st.title("Inventory Data Cleaner")

# REQUIRED COLUMNS (original names)
REQUIRED_COLUMNS = ["Item","Descript","Status Current","Replen Cls","Special Inst",
                    "Std UOM","End Use Code","Qty On Hand","Qty Avail","Curr Year Usage",
                    "Manufacturer Name","Mfg ID","Mfg Itm ID","Vendor Name","Currency",
                    "Unit Cost","Code","Comm Code", "MSDS ID"]

# Function to clean the data
def clean_inventory(df):
    # remove whitespace
    df.columns = df.columns.str.strip()
    
    # keep only required columns
    available_cols = [col for col in REQUIRED_COLUMNS if col in df.columns]
    df = df[available_cols]
    
    # clean numeric columns
    numeric_cols = ["Qty On Hand", "Qty Avail", "Unit Cost", "Curr Year Usage"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (df[col].astype(str).str.replace(",", "", regex=False).str.replace("$", "", regex=False))
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # drop completely empty rows
    df = df.dropna(how="all")
    df = df.reset_index(drop=True)
    return df

# File uploader
uploaded_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])
if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="latin1")
    else:
        df = pd.read_excel(uploaded_file)

    # keep original column names for display
    original_columns = df.columns.tolist()

    # make a cleaned copy for calculations
    df_clean = df.copy()
    df_clean.columns = (
        df_clean.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    st.success("File loaded successfully!")

    # show original columns
    column_table = pd.DataFrame(original_columns, columns=["Column Name"])
    st.subheader("Inventory Columns")
    with st.expander("Click to view columns"):
        st.dataframe(column_table, use_container_width=True, height=400)

    # clean data for preview
    cleaned = clean_inventory(df)

    st.subheader("Cleaned Data")
    st.dataframe(cleaned)

    st.download_button(
        "Download Cleaned CSV",
        cleaned.to_csv(index=False),
        "cleaned_inventory.csv",
        "text/csv"
    )

    # DISUTILITY MODEL WORK
    st.subheader("EOQ & Disutility Settings")

    ordering_cost = st.number_input(
        "Ordering cost per order (S)", min_value=0.0, value=100.0, step=1.0
    )

    holding_rate = st.slider(
        "Annual holding cost rate (%)", min_value=0, max_value=100, value=20
    ) / 100  # convert % to decimal

    # make sure numeric columns exist for calculation
    for col in ["curr_year_usage", "unit_cost"]:
        if col not in df_clean.columns:
            st.error(f"Missing column for calculation: {col}")
            st.stop()

    # EOQ calculations
    df_clean["annual_demand"] = df_clean["curr_year_usage"]
    df_clean["holding_cost"] = df_clean["unit_cost"] * holding_rate
    df_clean["EOQ"] = np.sqrt(
        (2 * df_clean["annual_demand"] * ordering_cost) / df_clean["holding_cost"]
    )

    # preview EOQ table
    display_cols = ["item", "qty_on_hand", "EOQ"]
    display_map = {
        c: original_columns[df.columns.get_loc(c)] if c in df.columns else c
        for c in df_clean.columns
    }

    st.subheader("EOQ Preview")
    st.dataframe(
        df_clean[display_cols].rename(columns=display_map),
        use_container_width=True,
        height=500
    )


