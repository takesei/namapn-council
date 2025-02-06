import streamlit as st
import pandas as pd

schemas = dict(
    item_axis=dict(
        finished_goods=False,
        item_types=False,
        items=False,
        materials=False,
        bom_trees=False,
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


def set_local(
    table: str, df: pd.DataFrame, original_df: pd.DataFrame | None = None
) -> None:
    if original_df is None:
        original_df = st.session_state.db.get(table)
    original_df[original_df.index.isin(df.index)] = df
    st.session_state.db.set_local(table, original_df)


axis = st.segmented_control("次元データ", schemas.keys(), selection_mode="single")
if axis is None:
    "# 軸未設定"
    "ここでは軸の按分/集計比率を変更します"
    "変更情報は同期ボタンを押すまでは全体に共有されません"
    st.info("上のボタンから対象となる軸を選択してください")
else:
    f"# {axis}"
    "ここでは軸の按分/集計比率を変更します"
    "変更情報は同期ボタンを押すまでは全体に共有されません"

    with st.spinner("データ取り込み中"):
        c1, c2 = st.columns(2, border=True)
        with c1:
            v_ax = st.session_state.db.get("versions")
            version = st.pills(
                "指定バージョン",
                ["ALL", *v_ax[v_ax.is_active].version.unique()],
                selection_mode="single",
                default="ALL",
            )
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
                cdf = st.data_editor(
                    df if version == "ALL" else df[df.version == version],
                    hide_index=False,
                    use_container_width=True,
                )
                if st.button(f"{table}を更新"):
                    with st.spinner():
                        set_local(table, cdf, df)
                        st.rerun()
        else:
            st.info("マスタデータを選択してください")
