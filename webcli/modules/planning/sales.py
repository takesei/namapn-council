import streamlit as st


"# 販売計画"
with st.spinner("loading"):
    df = st.session_state.db.get("sales_forecasts")
    df
