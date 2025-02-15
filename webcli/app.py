import streamlit as st
import vertexai

from libs import cache as C
from libs.typing import EventScenario

# Setup Streamlit Pages
st.set_page_config(
    page_title="Namaph Council Demo",
    page_icon=":material/forest:",
    layout="wide",
    # initial_sidebar_state="collapsed",
)
pages = C.load_navigation()
pg = st.navigation(pages)

# Init ai connection
vertexai.init(project="velvety-outcome-448307-f0", location="us-central1")

if "agent" not in st.session_state:
    st.session_state.agent = C.setup_aiagent()
# set jinja templates
if "jinja" not in st.session_state:
    st.session_state.jinja = C.set_template("./templates")


# Create DB connection
if "db" not in st.session_state:
    st.session_state.db = C.get_data_catalog("./dwh.duckdb")
    st.session_state.agent["event"] = EventScenario.from_dict(
        st.session_state.db.get("event_scenario")
    )

if "datahub" not in st.session_state:
    st.session_state.datahub = C.get_datahub(st.session_state.db)

if st.session_state.agent["event"] is not None:
    with st.sidebar:
        with st.container(border=True):
            st.error("**緊急対応**", icon="⚠️")
            st.page_link(
                "./modules/top/contingency_plan/main.py",
                label="台風上陸による調達計画影響",
            )

# Start streamlit app
pg.run()
