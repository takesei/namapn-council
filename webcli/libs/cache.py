from importlib import resources

import streamlit as st
import tomllib
import yaml
from jinja2 import Environment, FileSystemLoader

from libs.datahub import DataHub
from libs.genai import StrategyAgent
from libs.store import DataCatalog
from libs.typing import EventScenario


@st.cache_data(show_spinner=True, persist=False)
def load_navigation():
    print("Load TOML File")
    with open("navigation.toml", "rb") as f:
        pages = tomllib.load(f)

    return {
        section_name: [st.Page(**attr) for attr in page_attrs]
        for section_name, page_attrs in pages.items()
    }


@st.cache_resource
def setup_aiagent():
    print("Create Gemiin Agent")

    return dict(
        model=StrategyAgent(),
        chat_history=[],
        status="deactive",
    )


@st.cache_resource
def fetch_event(_db: DataCatalog):
    print("Check events")
    event = st.session_state.db.get("event_scenario")

    if event is not None:
        return EventScenario.from_dict(st.session_state.db.get("event_scenario"))
    else:
        return None


@st.cache_resource
def set_template(path: str):
    print("Load Templates")
    env = Environment(loader=FileSystemLoader(path), trim_blocks=True)
    return env


@st.cache_resource
def get_datahub(_db: DataCatalog):
    print("Create DataHub")
    return DataHub(_db)


@st.cache_resource
def get_data_catalog(db: str):
    print("Create DB Session")
    file_path = resources.files("libs.tables").joinpath("schema.yml")
    with file_path.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)["mart"]
    catalog = DataCatalog(db, schema)

    return catalog
