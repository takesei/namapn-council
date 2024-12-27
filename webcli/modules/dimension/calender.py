import streamlit as st

db = st.session_state.db

if "year" not in st.session_state:
    st.session_state.year = db.sql("select * from year").df()

if "month" not in st.session_state:
    st.session_state.month = db.sql("select * from month").df()

if "week" not in st.session_state:
    st.session_state.week = db.sql("select * from week").df()
    st.session_state.week = st.session_state.week.assign(
        ratio=(
            st.session_state.week.woking_days / st.session_state.week.woking_days.sum()
        )
    )

st.markdown("""# 品目軸
ここでは軸の按分/集計比率を変更します
""")

st.markdown("## Year")
st.dataframe(st.session_state.year, hide_index=True)

st.markdown("## Month")
st.session_state.month = st.data_editor(st.session_state.month, hide_index=True)

st.markdown("## Week")
st.session_state.week = st.data_editor(st.session_state.week, hide_index=True)

st.markdown("## Result")
df = st.session_state.month.join(st.session_state.week.set_index("month"), on="month")
st.session_state.calender = df
st.dataframe(df, hide_index=True)

