import streamlit as st

from src.collection_app.collection import Daily_Collection


def details():
    st.title(":blue[Customer Details]")
    Daily_Collection()

