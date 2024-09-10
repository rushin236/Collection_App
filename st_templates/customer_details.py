import streamlit as st

from src.collection_app.collection import Daily_Collection


def details():
    st.title(":blue[Customer Details]")

    st.subheader("Select Customer:")

    st.subheader("Name:")
    customer = st.selectbox(
        label="Customer Name",
        label_visibility="hidden",
        options=Daily_Collection().get_customer_names(),
    )

    name_col, amount_col, location_col = st.columns(spec=3, gap="large")

    with name_col:
        st.subheader("Name:")
        customer = st.text_input(
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

    # Initialize session state for authentication and input fields if not present
    if "authenticate" not in st.session_state:
        st.session_state.authenticate = False
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "pswd" not in st.session_state:
        st.session_state.pswd = ""

    # Define a function to reset the user and password
    def reset_auth_fields():
        st.session_state.user = ""
        st.session_state.pswd = ""

    def toggle_update():
        return not st.session_state.authenticate

    # Update button to trigger authentication process
    update_btn = st.button(label="Update Values", use_container_width=True)

    # Check if the update button is clicked or the session is authenticated
    if update_btn or toggle_update():

        # Popover for authentication input
        with st.expander("Authentication", expanded=True):
            # Display input fields with values from session state
            user = st.text_input(
                label="User:", value=st.session_state.user, key="user_input"
            )
            pswd = st.text_input(
                label="Password:",
                type="password",
                value=st.session_state.pswd,
                key="pswd_input",
            )

            auth_btn = st.button("Authenticate")

            if auth_btn:
                # Perform authentication
                auth = Daily_Collection().get_auth(user=user, pswd=pswd)

                if auth:
                    # Call update function on success
                    results = Daily_Collection().update_customer(
                        customer_name=customer,
                        customer_collection=amount,
                        location=location,
                    )
                    st.success(results)

                    # Reset user and password on success
                    reset_auth_fields()
                    st.session_state.authenticate = False

                else:
                    # Display warning on failure
                    st.warning("User name or password is invalid.")

                    # Reset user and password on failure
                    reset_auth_fields()
                    st.session_state.authenticate = False
