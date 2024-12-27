import streamlit as st
import pandas as pd


target_file = "data/sales/dim/product.csv"

if "supply_plan" not in st.session_state:
    supply_plan = pd.read_csv(target_file, index_col="id")
else:
    supply_plan = st.session_state.supply_plan


def run_simulator(path: str) -> pd.DataFrame:
    st.session_state.supply_plan = pd.read_csv(path)


st.data_editor(supply_plan, num_rows="dynamic")
