import streamlit as st

db = st.session_state.db

plant = db.sql("select * from plant").df()

if "storage" not in st.session_state:
    st.session_state.storage = db.sql("select * from storage").df()

st.markdown("""# 組織軸
ここでは軸の按分/集計比率を変更します
""")

st.markdown("## Plant")
st.dataframe(plant, hide_index=True)

st.markdown("## Storage")
st.session_state.storage = st.data_editor(st.session_state.storage, hide_index=True)


st.markdown("## Result")
df = plant.join(st.session_state.storage.set_index("plant_code"), on="plant_code")
st.session_state.logistics = df
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
