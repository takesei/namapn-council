import streamlit as st

"# Instant BI"

"## Supply Plan"
st.session_state.sp

df = (
    st.session_state.sp.loc[
        :, ["jan_code", "annex_id", "prod_cost", "store_cost", "transportatoin_cost"]
    ]
    .groupby(["jan_code", "annex_id"])
    .sum()
    .reset_index()
)

st.bar_chart(df, y=["prod_cost", "store_cost", "transportatoin_cost"])

"## Sales Plan"
st.session_state.dp
df = st.session_state.dp

st.bar_chart(df, y=["order_yen", "sales_expenses_yen"])

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
