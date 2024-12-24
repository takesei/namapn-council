import streamlit as st
import pandas as pd


# Preparation
def update(df):
    st.session_state.df_p = df
    print(df)


df_original = pd.DataFrame(
    [["A", 100], ["B", 200]],
    columns=["parent", "quantity"],
)

if "df_p" not in st.session_state:
    df_p = pd.DataFrame(
        [["A", "a1", 0.7], ["A", "a2", 0.3], ["B", "b1", 1.0]],
        columns=["parent", "child", "ratio"],
    )
else:
    df_p = st.session_state.df_p


# Content
st.markdown("# 按分ロジックDemo")

st.markdown("## 比率マスタ")
df_p = st.data_editor(df_p, num_rows="dynamic")
df_merged = pd.merge(df_p, df_original, on=["parent"])
df_merged.quantity *= df_merged.ratio


st.markdown("## 粒度変更処理")
c1, c2 = st.columns(2, border=True)
with c1:
    st.markdown("### 按分")
    st.markdown("元ネタ")
    st.dataframe(df_original)
    st.markdown("結果")
    st.dataframe(df_merged)
with c2:
    st.markdown("### 集計")
    st.markdown("元ネタ")
    st.dataframe(df_merged.drop(columns=["parent", "ratio"]))
    st.markdown("結果")
    st.dataframe(df_original)
