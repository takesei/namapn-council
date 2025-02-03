import streamlit as st
import pandas as pd
import time


def optimize():
    with st.spinner("optimizing..."):
        time.sleep(1)
    st.success("Done!")
    df = st.session_state.sp
    psi = st.session_state.psi
    st.session_state.sp.prod_cost = df.jan_code * (4 - (df.annex_id % 4)) * psi.P * 0.8
    st.session_state.sp.store_cost = psi.I * (df.annex_id % 4) * 0.7
    st.session_state.sp.transportatoin_cost = psi.P * (df.annex_id % 4) * 1.5


if "sp" not in st.session_state:
    df = st.session_state.dp.loc[
        :,
        [
            "jan_code",
            "jan_name",
            "hq_code",
            "hq_name",
            "month",
            "week_of_month",
            "quantity",
        ],
    ]
    df = pd.merge(df, st.session_state.annex, on="hq_code")
    df.quantity *= df.ratio
    df = df.drop(columns=["hq_code", "hq_name", "ratio"])
    df = df.assign(prod_cost=None, store_cost=None, transportatoin_cost=None)
    st.session_state.sp = df

st.session_state.sp = st.data_editor(st.session_state.sp)
st.button("optimize", on_click=optimize)
