import streamlit as st
import pandas as pd


schemas = st.session_state.db.schema["dimension"]


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
            v_ax = v_ax[v_ax.is_active].sort_values("version_code")
            tag = v_ax.version_code + ":" + v_ax.version_name
            version = st.pills(
                "指定バージョン", ["ALL", *tag], selection_mode="single", default="ALL"
            )
        with c2:
            tables = st.pills(
                "マスタデータ(複数選択可)",
                schemas[axis],
                selection_mode="multi",
                default=schemas[axis][0],
            )
        if version is None:
            st.info("version情報が選択されていません")
            st.stop()

        version = version.split(":")[0]

        if len(tables) > 0:
            for table in tables:
                st.markdown(f"## {table}")
                df = st.session_state.db.get(table)
                cdf = st.data_editor(
                    df[df.version == version]
                    if "version" in df.columns and version != "ALL"
                    else df,
                    hide_index=False,
                    use_container_width=True,
                )
                if st.button(f"{table}を更新"):
                    with st.spinner():
                        set_local(table, cdf, df)
                        st.rerun()
        else:
            st.info("マスタデータを選択してください")
