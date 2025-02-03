import streamlit as st

schemas = dict(
    bom_trees=False,
    transaction_types=False,
    transactions=False,
)

forecast = st.segmented_control("過去実績", schemas.keys(), selection_mode="single")
if forecast is None:
    "# 過去実績"
    "ここでは過去実績を分析します"
    st.info("上のボタンから対象となる過去実績を選択してください")
else:
    f"# {forecast}"
    "ここでは過去実績を分析します"

    with st.spinner("データ取り込み中"):
        version = st.pills(
            "指定バージョン",
            ["ALL", *st.session_state.db.get("versions").version.unique()],
            selection_mode="single",
            default="ALL",
        )
        if version is None:
            st.info("version情報が選択されていません")

        st.markdown(f"## {forecast}")
        df = st.session_state.db.get(forecast)
        st.data_editor(
            df if version == "ALL" else df[df.version == version],
            hide_index=True,
            use_container_width=True,
        )
