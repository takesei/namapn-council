import streamlit as st


if "psi" not in st.session_state:
    st.session_state.psi = (
        st.session_state.sp.loc[
            :,
            [
                "jan_code",
                "jan_name",
                "month",
                "week_of_month",
                "annex_id",
                "annex_name",
                "quantity",
            ],
        ]
        .rename(columns=dict(quantity="S"))
        .assign(I=0, P=0)
    )

if "safety_margin_weeks" not in st.session_state:
    st.session_state.safety_margin_weeks = 2

st.session_state.safety_margin_weeks = st.number_input(
    "安全在庫週数",
    value=st.session_state.safety_margin_weeks,
    min_value=0,
    max_value=5,
    step=1,
)

df = st.session_state.psi

for i in range(1, 10):
    d = df[df.annex_id == i]
    f"annex id:{i} | {d.annex_name.unique()[0]}"
    d = d.drop(columns=["annex_id", "annex_name"])
    d.I = (
        d.S[::-1]
        .rolling(st.session_state.safety_margin_weeks, min_periods=0)
        .sum()[::-1]
    )
    d.P = d.S.values + d.I.values - [0, *(d.I[:-1].values)]
    df.loc[d.index, ["P", "S", "I"]] = d.loc[d.index, ["P", "S", "I"]]
    st.data_editor(d)

st.session_state.psi = df
st.session_state.psi
