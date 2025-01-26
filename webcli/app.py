import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
import tomllib
import duckdb
import os

# Page Config
st.set_page_config(
    page_title="Namaph Council Demo",
    page_icon=":material/forest:",
    layout="wide",
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

# Init ai connection
vertexai.init(project="velvety-outcome-448307-f0", location="us-west1")
st.session_state.aiagent = GenerativeModel("gemini-1.5-flash-002")
st.session_state.aisession = st.session_state.aiagent.start_chat()


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

    with st.sidebar:
        with st.container(border=True):
            st.error("**緊急対応**", icon="⚠️")
            st.page_link(
                "./modules/bi/contingency_plan.py",
                label="台風上陸による調達計画影響",
            )
            st.page_link(
                "./modules/bi/contingency_plan.py",
                label="SNS反響による急激な需要変化",
            )

except Exception as e:
    print("Failed to construct navigation")
    raise e

pg.run()
