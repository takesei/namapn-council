import streamlit as st
import pandas as pd


if "bp" not in st.session_state:
    df1 = pd.merge(st.session_state.brand, st.session_state.channel, how="cross")
    df2 = pd.merge(
        st.session_state.branch.drop(columns=["region_code", "ratio"]),
        st.session_state.year,
        how="cross",
    )

    st.session_state.bp = pd.merge(df1, df2, how="cross").assign(order_yen=1000000)

"# 年間計画"

st.session_state.bp = st.data_editor(st.session_state.bp)
f"{st.session_state.bp.order_yen.sum()}"

st.bar_chart(st.session_state.bp, y="order_yen", x_label="Num", y_label="Order[yen]")

st.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")

st.metric(label="Active developers", value=123, delta=123, delta_color="off")


col1, col2, col3 = st.columns(3)
col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")

a, b = st.columns(2)
c, d = st.columns(2)

a.metric("Temperature", "30°F", "-9°F", border=True)
b.metric("Wind", "4 mph", "2 mph", border=True)

c.metric("Humidity", "77%", "5%", border=True)
d.metric("Pressure", "30.34 inHg", "-2 inHg", border=True)
