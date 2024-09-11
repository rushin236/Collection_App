import streamlit as st
from streamlit_option_menu import option_menu

from st_templates.add_collection import AddCollection
from st_templates.add_customer import AddCustomer
from st_templates.customer_details import CustomerDetails

st.set_page_config(layout="wide")

selected = option_menu(
    menu_title="Collection App",
    options=["Collection", "Details", "Add"],
    orientation="horizontal",
    default_index=0,
)

if selected == "Collection":
    AddCollection()

elif selected == "Details":
    CustomerDetails()

elif selected == "Add":
    AddCustomer()
