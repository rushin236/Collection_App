import streamlit as st

from src.collection_app.collection import Daily_Collection


def get_authentication(user, pswd):
    auth = Daily_Collection().get_auth(user=user, pswd=pswd)
    return auth


def user_pass_state():
    if "user" not in st.session_state:
        st.session_state.user = ""

    if "passward" not in st.session_state:
        st.session_state.passward = ""


def reset_cred():
    st.session_state.user = ""
    st.session_state.passward = ""


def CustomerDetails():
    st.title(":blue[Customer Details]")

    st.subheader("Select Customer:")

    st.subheader("Name:")
    customer = st.selectbox(
        label="Customer Name",
        label_visibility="hidden",
        options=Daily_Collection().get_customer_names(),
    )

    name_col, amount_col, location_col, update_check = st.columns(spec=4, gap="large")

    with name_col:
        st.subheader("Name:")
        name = st.text_input(
            label="Customer Name",
            label_visibility="hidden",
            value=Daily_Collection().get_name(customer=customer),
        )

    with amount_col:
        st.subheader("Amount:")
        amount = st.number_input(
            label="Amount",
            label_visibility="hidden",
            min_value=10,
            value=Daily_Collection().get_daily_amount(customer=customer),
        )

    with location_col:
        st.subheader("Location:")
        location = st.text_input(
            label="Customer Location",
            label_visibility="hidden",
            value=Daily_Collection().get_location(customer=customer),
        )

    with update_check:
        st.subheader("Update")
        update_select = st.selectbox(
            label="Update Select",
            label_visibility="hidden",
            options=["No", "Yes"],
        )

    if update_select == "Yes":
        with st.expander(label="Authenticate"):

            user_pass_state()

            user_name = st.text_input(label="User Name", value=st.session_state.user)

            user_pass = st.text_input(
                label="User Passward", value=st.session_state.passward, type="password"
            )

            auth_btn = st.button(label="Authenticate", use_container_width=True)
            if auth_btn:
                auth = get_authentication(user=user_name, pswd=user_pass)

                if auth:
                    # Call update function on success
                    results = Daily_Collection().update_customer(
                        customer=customer,
                        name=name,
                        customer_collection=amount,
                        location=location,
                    )
                    st.success(results)

                    # Reset user and password on success
                    reset_cred()

                else:
                    # Display warning on failure
                    st.warning("User name or password is invalid.")

                    # Reset user and password on failure
                    reset_cred()
