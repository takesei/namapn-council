import streamlit as st

db = st.session_state.db

if "channel" not in st.session_state:
    st.session_state.channel = db.sql("select * from channel").df()

if "hq" not in st.session_state:
    st.session_state.hq = db.sql("select * from hq").df().assign(ratio=[0.5, 0.5, 1, 1])

if "annex" not in st.session_state:
    st.session_state.annex = (
        db.sql("select * from annex")
        .df()
        .assign(ratio=[0.5, 0.5, 1, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5])
    )

st.markdown("""# 組織軸
ここでは軸の按分/集計比率を変更します
""")

st.markdown("## Channel")
st.dataframe(st.session_state.channel, hide_index=True)

st.markdown("## Hq")
st.session_state.hq = st.data_editor(st.session_state.hq, hide_index=True)

st.markdown("## Annex")
st.session_state.annex = st.data_editor(st.session_state.annex, hide_index=True)


st.markdown("## Result")
df = st.session_state.channel.join(st.session_state.hq.set_index("channel_code"), on="channel_code")
df = df.join(st.session_state.annex.set_index("hq_code"), on="hq_code", lsuffix="_")
df.ratio *= df.ratio_
df = df.drop(columns=["ratio_"])
st.session_state.customer = df
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
