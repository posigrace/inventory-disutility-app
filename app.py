import streamlit as st
import pandas as pd
import re

st.title("Inventory Data Cleaner")

#REQUIRED COLUMNS
REQUIRED_COLUMNS = [
    "Item",
    "Descript",
    "Status Current",
    "Replen Cls",
    "Special Inst",
    "Std UOM",
    "End Use Code",
    "Qty On Hand",
    "Qty Avail",
    "Manufacturer Name",
    "Mfg ID",
    "Mfg Itm ID",
    "Vendor Name",
    "Currency",
    "Unit Cost",
    "Code",
    "Comm Code",
    "MSDS ID"
]

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

    st.subheader("Original Columns")
    st.write(df.columns.tolist())

    cleaned = clean_inventory(df)

    st.subheader("Cleaned Data")
    st.dataframe(cleaned)

    st.download_button(
        "Download Cleaned CSV",
        cleaned.to_csv(index=False),
        "cleaned_inventory.csv",
        "text/csv"
    )


