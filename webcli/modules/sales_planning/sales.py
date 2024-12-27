import streamlit as st
import pandas as pd
import numpy as np


def inference(df):
    df.quantity = df.order_yen / (5 * df.jan_code)
    df.sales_expenses_yen = df.jan_code + (300 + 200 * (1 + np.random.randn(len(df))))
    st.session_state.dp = df


if "dp" not in st.session_state:
    year_week = st.session_state.calender.loc[
        :, ["year", "month", "week_of_month", "ratio"]
    ]

    df = st.session_state.bp
    df = pd.merge(df, st.session_state.jan, on=["brand_code"])
    df.order_yen *= df.ratio
    df = df.drop(columns=["brand_code", "brand_name", "ratio"])

    df = pd.merge(df, st.session_state.hq, on=["channel_code"])
    df.order_yen *= df.ratio
    df = df.drop(columns=["channel_code", "channel_name", "ratio"])

    df = pd.merge(df, st.session_state.section, on=["branch_code"])
    df.order_yen *= df.ratio
    df = df.drop(columns=["branch_code", "branch_name", "ratio"])

    df = pd.merge(df, year_week, on=["year"])
    df.order_yen *= df.ratio * 2  # i dont know why
    df = df.drop(columns=["year", "ratio"])
    df = df.assign(quantity=None, sales_expenses_yen=None)
    st.session_state.dp = df

"# 販売計画"
st.session_state.dp = st.data_editor(st.session_state.dp)

st.button("必要営業費用推定", on_click=inference, args=[st.session_state.dp])

st.bar_chart(st.session_state.dp, y="order_yen", x_label="Num", y_label="Order[yen]")
