import streamlit as st
import pandas as pd
import os

st.title("Inventory Prototype – Test Run")

if os.path.exists("inventory.xlsx"):
    df = pd.read_excel("inventory.xlsx")
    st.write("Excel loaded successfully.")
    df = df.head(5)

    for _, row in df.iterrows():
    	st.subheader(row["Descript"])

    	st.caption(f"Location: {row['Area']} / {row['Lev 1']}")

    	st.write("Qty On Hand:", row["Qty On Hand"])
    	st.write("Qty Available:", row["Qty Avail"])
    	st.write("Reorder Point:", row["Reorder Pt"])

    	if row["Qty Avail"] < row["Reorder Pt"]:
        	st.warning("Below reorder point")
    	else:
        	st.success("Stock level OK")

    	st.divider()
else:
    st.error("inventory.xlsx not found in this folder.")
