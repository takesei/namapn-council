import streamlit as st
import tomllib

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


# Navigation
try:
    pg = st.navigation(pages)
except Exception as e:
    print("Failed to construct navigation")
    raise e

pg.run()
