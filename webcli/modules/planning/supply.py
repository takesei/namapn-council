import streamlit as st


"# 供給計画"
with st.spinner("loading"):
    df = st.session_state.db.get("production_forecasts")
    df
