import streamlit as st

schemas = dict(
    production_forecasts=False,
    resource_forecasts=False,
    routing_forecasts=False,
    sales_forecasts=False,
)

forecast = st.segmented_control("AI予測情報", schemas.keys(), selection_mode="single")
if forecast is None:
    "# AI予測未設定"
    "ここではAI予測結果を分析します"
    st.info("上のボタンから対象となるAI予測情報を選択してください")
else:
    f"# {forecast}"
    "ここではAI予測結果を分析します"

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
