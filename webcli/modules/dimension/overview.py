import streamlit as st

"# 按分/集計 比率 設定状況"

for i in ["product", "organization", "customer", "calender", "logistics"]:
    st.markdown(f"**{i.capitalize()}軸**")
    df = st.session_state.get(i)
    if df is None:
        "未設定です"
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "ratio": st.column_config.ProgressColumn(
                "Ratio",
                help="The ratio volume",
                format="%.2f",
                min_value=0,
                max_value=1,
                pinned=True,
            ),
        },
    )
