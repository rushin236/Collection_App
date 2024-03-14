import streamlit as st

from src.collection_app.collection import Daily_Collection


def AddCollection():
    st.title(":blue[Collection]")

    date_col, name_col, amount_col = st.columns(spec=3, gap="large")

    with date_col:
        st.subheader("Date:")
        date = st.date_input(
            label="Date", label_visibility="hidden", value="today", format="DD/MM/YYYY"
        )

    with name_col:
        st.subheader("Name:")
        customer = st.selectbox(
            label="Customer Name",
            label_visibility="hidden",
            options=Daily_Collection().get_customer_names(),
        )

    with amount_col:
        st.subheader("Amount:")
        amount = st.number_input(
            label="Amount",
            label_visibility="hidden",
            min_value=10,
            value=int(Daily_Collection().get_daily_amount(customer=customer)),
        )

    submit_btn = st.button(label="Submit")

    if submit_btn:
        response = Daily_Collection().add_collection(
            date=date, customer=customer, amount=amount
        )

        st.success(response)

