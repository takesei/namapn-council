import streamlit as st


"# 調達計画"
with st.spinner("loading"):
    df = st.session_state.db.get("resource_forecasts")
    df
