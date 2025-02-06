import streamlit as st


pred_schemas = dict(
    production_forecasts=False,
    resource_forecasts=False,
    routing_forecasts=False,
    sales_forecasts=False,
)

tran_schemas = dict(
    transaction_types=False,
    transactions=False,
)

forecasts = st.segmented_control("AI予測", pred_schemas.keys(), selection_mode="multi")
trans = st.segmented_control("実績", tran_schemas.keys(), selection_mode="multi")

if len(forecasts) == 0 and len(trans) == 0:
    "# 情報未選択"
    "ここではAI予測結果や過去実績を分析します"
    st.info("上のボタンから対象となるAI予測情報を選択してください")
else:
    f"# {' vs '.join([f'`{v}`' for v in forecasts + trans])}"
    "ここではAI予測結果や過去実績を分析します"

    with st.spinner("データ取り込み中"):
        c1, c2 = st.columns(2, border=True)
        with c1:
            v_ax = st.session_state.db.get("versions")
            versions = st.pills(
                "指定バージョン",
                v_ax[v_ax.is_active].version.unique(),
                selection_mode="multi",
                default=v_ax.version.unique()[0],
            )
        with c2:
            viz = st.segmented_control(
                "表示方法",
                ["line_chart", "bar_chart", "table"],
                selection_mode="single",
                default="line_chart",
            )
        if len(versions) == 0:
            st.info("version情報が選択されていません")
            st.stop()

        match viz:
            case "table":
                for forecast in forecasts:
                    df = st.session_state.db.get(forecast)
                    for version in versions:
                        f"## {forecast}[{version}]"
                        st.dataframe(
                            df[df.version == version], use_container_width=True
                        )
            case "line_chart":
                chart = None
                for forecast in forecasts:
                    df = st.session_state.db.get(forecast)
                    x_ax, y_ax = "", ""
                    if "month" in df.columns:
                        x_ax = "month"
                    elif "date" in df.columns:
                        x_ax = "date"
                    if "quantity" in df.columns:
                        y_ax = "quantity"
                    elif "capacity" in df.columns:
                        y_ax = "capacity"
                    for version in versions:
                        data = df.loc[df.version == version, [x_ax, y_ax]].set_index(x_ax)
                        if chart is None:
                            chart = st.line_chart(data)
                        else:
                            chart.add_rows(data)
