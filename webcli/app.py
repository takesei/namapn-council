import streamlit as st
import tomllib
import duckdb
import os

# Page Config
st.set_page_config(
    page_title="Namaph Council Demo",
    page_icon=":material/forest:",
)


# Load Navigation config
@st.cache_data(show_spinner=True, persist=False)
def load_navigation():
    print("Load TOML File")
    try:
        with open("navigation.toml", "rb") as f:
            pages = tomllib.load(f)
    except Exception as e:
        print("Toml parsing failed")
        raise e

    return {
        section_name: [st.Page(**attr) for attr in page_attrs]
        for section_name, page_attrs in pages.items()
    }


pages = load_navigation()


# Create DB connection
@st.cache_resource
def duckdb_local_session(db: str):
    print("Create DB Session")
    con = duckdb.connect(database=db)

    return con


def fetch_data():
    return None


if "db" not in st.session_state:
    st.session_state.db = duckdb_local_session("./dwh.duckdb")

if "data_fetched" not in st.session_state:
    print("Fetch data")
    os.makedirs("data", exist_ok=True)
    msg = st.toast("データ更新中", icon=":material/sync:")
    err = fetch_data()
    if err is None:
        msg.toast("データ更新完了, good luck!!", icon=":material/check:")
        st.session_state.data_fetched = True
    else:
        msg.toast("データ更新失敗, try again later", icon=":material/block:")

# Navigation
try:
    pg = st.navigation(pages)
except Exception as e:
    print("Failed to construct navigation")
    raise e

pg.run()
