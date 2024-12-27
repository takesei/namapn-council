import streamlit as st

db = st.session_state.db

if "brand" not in st.session_state:
    st.session_state.brand = db.sql("select * from brand").df()

if "jan" not in st.session_state:
    st.session_state.jan = db.sql("select * from jan").df().assign(ratio=[0.5, 0.5, 1])

if "sku" not in st.session_state:
    st.session_state.sku = (
        db.sql("select * from sku").df().assign(ratio=[0.5, 0.5, 0.5, 0.5, 1])
    )

st.markdown("""# 品目軸
ここでは軸の按分/集計比率を変更します
""")

st.markdown("## Brand")
st.dataframe(st.session_state.brand, hide_index=True)

st.markdown("## JAN")
st.session_state.jan = st.data_editor(st.session_state.jan, hide_index=True)

st.markdown("## SKU")
st.session_state.sku = st.data_editor(st.session_state.sku, hide_index=True)

st.markdown("## Result")
df = st.session_state.brand.join(st.session_state.jan.set_index("brand_code"), on="brand_code")
df = df.join(st.session_state.sku.set_index("jan_code"), on="jan_code", lsuffix="_")
df.ratio *= df.ratio_
df = df.drop(columns=["ratio_"])
st.session_state.product = df
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
