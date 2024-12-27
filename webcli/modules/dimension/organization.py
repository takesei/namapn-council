import streamlit as st

db = st.session_state.db

region = db.sql("select * from region").df()

if "branch" not in st.session_state:
    st.session_state.branch = (
        db.sql("select * from branch").df().assign(ratio=[0.5, 0.5])
    )

if "section" not in st.session_state:
    st.session_state.section = (
        db.sql("select * from section").df().assign(ratio=[0.34, 0.33, 0.33, 0.5, 0.5])
    )

st.markdown("""# 組織軸
ここでは軸の按分/集計比率を変更します
""")

st.markdown("## Region")
st.dataframe(region, hide_index=True)

st.markdown("## Branch")
st.session_state.branch = st.data_editor(st.session_state.branch, hide_index=True)

st.markdown("## Section")
st.session_state.section = st.data_editor(st.session_state.section, hide_index=True)


st.markdown("## Result")
df = region.join(st.session_state.branch.set_index("region_code"), on="region_code")
df = df.join(
    st.session_state.section.set_index("branch_code"), on="branch_code", lsuffix="_"
)
df.ratio *= df.ratio_
df = df.drop(columns=["ratio_"])
st.session_state.organization = df
st.dataframe(
    df,
    hide_index=True,
    column_config={
        "ratio": st.column_config.ProgressColumn(
            "Ratio",
            help="The ratio volume",
            format="%f",
            min_value=0,
            max_value=1,
            pinned=True,
        ),
    },
)
