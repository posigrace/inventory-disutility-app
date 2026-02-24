import streamlit as st
import pandas as pd
import re

st.title("Inventory Data Cleaner")

#REQUIRED COLUMNS
REQUIRED_COLUMNS = ["Item","Descript","Status Current","Replen Cls","Special Inst","Std UOM","End Use Code","Qty On Hand","Qty Avail","Manufacturer Name","Mfg ID","Mfg Itm ID","Vendor Name","Currency","Unit Cost","Code","Comm Code", "MSDS ID"]

#function to clean the data
def clean_inventory(df):

     # remove whitespace
    df.columns = df.columns.str.strip()
    
     # keep only required columns
    available_cols = [col for col in REQUIRED_COLUMNS if col in df.columns]
    df = df[available_cols]
    
    # clean numeric columns
    numeric_cols = ["Qty On Hand", "Qty Avail", "Unit Cost"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False) 
                    )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # drop completely empty rows
    df = df.dropna(how="all")

    df = df.reset_index(drop=True)

    return df

#file uploader
uploaded_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])
if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="latin1")
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = (df.columns
        .str.strip()                        # remove spaces at start/end
        .str.lower()                        # lowercase everything
        .str.replace(" ", "_")              # replace spaces with underscores
        .str.replace(r"[^\w]", "", regex=True)  # remove special characters
    )
    st.success("File loaded successfully!")

    
    column_table = pd.DataFrame(df.columns, columns=["Column Name"])
    st.subheader("Inventory Columns")

    with st.expander("Click to view columns"):
        st.dataframe(column_table, use_container_width=True, height=400)

    cleaned = clean_inventory(df)

    st.subheader("Cleaned Data")
    st.dataframe(cleaned)

    st.download_button(
        "Download Cleaned CSV",
        cleaned.to_csv(index=False),
        "cleaned_inventory.csv",
        "text/csv" )

#DISUTILITY MODEL WORK
st.subheader("EOQ & Disutility Settings")

ordering_cost = st.number_input(
    "Ordering cost per order (S)", min_value=0.0, value=100.0, step=1.0)

holding_rate = st.slider(
    "Annual holding cost rate (%)", min_value=0, max_value=100, value=20) / 100  # convert % to decimal

df["annual_demand"] = df["Curr Year Usage"]
df["holding_cost"] = holding_rate * df["Unit Cost"]

import numpy as np

df["EOQ"] = np.sqrt(
    (2 * df["annual_demand"] * ordering_cost) / df["holding_cost"])

st.subheader("EOQ Preview")
st.dataframe(
    df[["Item", "Qty On Hand", "EOQ"]],
    use_container_width=True,
    height=500
)

