import streamlit as st
import pandas as pd


# Preparation
df_original = pd.DataFrame(
    [["A", 100], ["B", 200]],
    columns=["parent", "quantity"],
)

df_p = pd.DataFrame(
    [["A", "a1", 0.7], ["A", "a2", 0.3], ["B", "b1", 1.0]],
    columns=["parent", "child", "ratio"],
)

# Content
"# 按分ロジックDemo"
"## 比率マスタ"
df_p = st.data_editor(df_p, num_rows="dynamic")
df_merged = pd.merge(df_p, df_original, on=["parent"])
df_merged.quantity *= df_merged.ratio


"## 粒度変更処理"
c1, c2 = st.columns(2, border=True)
with c1:
    "### 按分"
    "元ネタ"
    st.dataframe(df_original)
    "結果"
    st.dataframe(df_merged)
with c2:
    "### 集計"
    "元ネタ"
    st.dataframe(df_merged.drop(columns=["parent", "ratio"]))
    "結果"
    st.dataframe(df_original)
