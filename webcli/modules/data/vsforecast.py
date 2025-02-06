import streamlit as st
import pandas as pd

forecast_tables = st.session_state.db.schema["forecast"]
transaction_tables = st.session_state.db.schema["transaction"]


forecasts = st.segmented_control("AI予測", forecast_tables, selection_mode="multi")
trans = st.segmented_control(
    "実績",
    ["transactions:Sales", "transactions:Purchase"],
    selection_mode="multi",
)

selections = forecasts + trans

if len(selections) == 0:
    "# 情報未選択"
    "ここではAI予測結果や過去実績を分析します"
    st.info("上のボタンから対象となるAI予測情報を選択してください")
else:
    f"# {' vs '.join([f'`{v}`' for v in selections])}"
    "ここではAI予測結果や過去実績を分析します"

    with st.spinner("データ取り込み中"):
        c1, c2 = st.columns(2, border=True)
        with c1:
            v_ax = st.session_state.db.get("versions")
            v_ax = v_ax[v_ax.is_active].sort_values("version_code")
            tag = v_ax.version_code + ":" + v_ax.version_name
            versions = st.pills(
                "指定バージョン", tag, selection_mode="multi", default=tag.iloc[0]
            )
            versions = [v.split(":")[0] for v in versions]
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
                for table in selections:
                    if table in ["transactions:Sales", "transactions:Purchase"]:
                        df = st.session_state.db.get("transactions")
                        table_type = table.split(":")[1]
                        df = df[df.transaction_type == table_type]
                    else:
                        df = st.session_state.db.get(table)
                    for version in versions:
                        f"## {table}[{version}]"
                        st.dataframe(
                            df[df.version == version], use_container_width=True
                        )
            case "line_chart":
                charts = []
                for table in selections:
                    if table in ["transactions:Sales", "transactions:Purchase"]:
                        df = st.session_state.db.get("transactions")
                        table_type = table.split(":")[1]
                        df = df[df.transaction_type == table_type]
                    else:
                        df = st.session_state.db.get(table)
                    df = df.loc[
                        df.version.isin(versions), ["time_id", "version", "quantity"]
                    ]
                    df.time_id = pd.to_datetime(df.time_id).dt.date
                    data = (
                        df.groupby(["time_id", "version"])
                        .sum()
                        .reset_index()
                        .set_index("time_id")
                    )
                    data.version = table + "-" + data.version
                    charts.append(data)
                summary = pd.concat(charts, axis=0)
                st.line_chart(summary, x=None, y="quantity", color="version")

            case "bar_chart":
                charts = []
                for table in selections:
                    if table in ["transactions:Sales", "transactions:Purchase"]:
                        df = st.session_state.db.get("transactions")
                        table_type = table.split(":")[1]
                        df = df[df.transaction_type == table_type]
                    else:
                        df = st.session_state.db.get(table)
                    df = df.loc[
                        df.version.isin(versions), ["time_id", "version", "quantity"]
                    ]
                    df.time_id = pd.to_datetime(df.time_id).dt.strftime("%Y/%m/%d")
                    data = (
                        df.groupby(["time_id", "version"])
                        .sum()
                        .reset_index()
                        .set_index("time_id")
                    )
                    data.version = table + "-" + data.version
                    charts.append(data)
                summary = pd.concat(charts, axis=0)
                st.bar_chart(
                    summary, x=None, y="quantity", color="version", stack=False
                )

            case _:
                st.info("表示方法を選択してください")
