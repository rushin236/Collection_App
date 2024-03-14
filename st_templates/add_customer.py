import streamlit as st

from src.collection_app.collection import Daily_Collection


def AddCustomer():
    st.title(":blue[Add Customer]")

    title_name, title_collection, title_location = st.columns(spec=3, gap="large")

    with title_name:
        st.subheader("Name:")
        customer_name = st.text_input(label="Customer Name", label_visibility="hidden")

    with title_collection:
        st.subheader("Amount:")
        daily_amount = st.number_input(
            label="Daily Amount", label_visibility="hidden", min_value=10, step=10
        )

    with title_location:
        st.subheader("Location:")
        customer_location = st.text_input(
            label="Customer Location", label_visibility="hidden"
        )

    submit_btn = st.button(label="Submit", use_container_width=True)

    inputs = {
        "Customer Name": customer_name,
        "Daily Collection": daily_amount,
        "Customer Location": customer_location,
    }

    if submit_btn:
        response = Daily_Collection().add_customer(
            inputs=inputs,
            customer_name=customer_name,
            daily_amount=int(daily_amount),
            customer_location=customer_location,
        )

        if response[0]:
            st.success(response[1])
        else:
            st.warning(response[1])

