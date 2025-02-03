import streamlit as st

schemas = dict(
    item_axis=dict(
        finished_goods=False,
        item_types=False,
        items=False,
        materials=False,
    ),
    customer_axis=dict(
        customers=False,
        retailers=False,
        suppliers=False,
    ),
    company_axis=dict(
        companies=False,
    ),
    plant_axis=dict(
        lines=False,
        locations=False,
        plants=False,
        storages=False,
    ),
    calender_axis=dict(
        months=False,
        dates=False,
        times=False,
        years=False,
    ),
    route_axis=dict(
        routing_forecasts=False,
        routings=False,
    ),
    version_axis=dict(
        versions=False,
    ),
)

axis = st.segmented_control("次元データ", schemas.keys(), selection_mode="single")
if axis is None:
    "# 軸未設定"
    "ここでは軸の按分/集計比率を変更します"
    st.info("上のボタンから対象となる軸を選択してください")
else:
    f"# {axis}"
    "ここでは軸の按分/集計比率を変更します"

    c1, c2 = st.columns(2, border=True)

    with st.spinner("データ取り込み中"):
        with c1:
            version = st.pills(
                "指定バージョン",
                ["ALL", *st.session_state.db.get("versions").version.unique()],
                selection_mode="single",
                default="ALL",
            )
            print(version)
        with c2:
            tables = st.pills(
                "マスタデータ(複数選択可)",
                schemas[axis].keys(),
                selection_mode="multi",
                default=list(schemas[axis].keys())[0],
            )
        if version is None:
            st.info("version情報が選択されていません")

        if len(tables) > 0:
            for table in tables:
                st.markdown(f"## {table}")
                df = st.session_state.db.get(table)
                st.data_editor(
                    df if version == "ALL" else df[df.version == version],
                    hide_index=True,
                    use_container_width=True,
                )
        else:
            st.info("マスタデータを選択してください")
