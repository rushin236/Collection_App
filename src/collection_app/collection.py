import gspread
import pandas as pd
import pywhatkit
import streamlit as st
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

client = gspread.authorize(creds)
workbook = client.open_by_key(st.secrets["private_gsheet_id"])


class Daily_Collection:
    def __init__(self) -> None:
        self.collection_sheet = workbook.worksheet("Collection")
        self.customer_sheet = workbook.worksheet("Customers")

    def get_customer_names(self):
        customer_names = self.customer_sheet.col_values(1)[1:]

        return customer_names

    def get_daily_amount(self, customer):
        location = self.customer_sheet.find(query=customer, in_column=1)
        daily_amount = self.customer_sheet.cell(row=location.row, col=2).value

        return daily_amount

    def add_customer(
        self,
        inputs: dict,
        customer_name: str,
        daily_amount: int,
        customer_location: str,
    ) -> tuple:
        try:
            customers_name = self.customer_sheet.col_values(1)[1:]
            if customer_name in customers_name:
                return (True, f"Customer: {customer_name} already exists in database.")

            elif ("" not in inputs.values()) and (customer_name not in customers_name):
                self.customer_sheet.append_row(
                    values=[customer_name, daily_amount, customer_location]
                )

                return (
                    True,
                    f"Added Customer: {customer_name}, Daily Collection: {daily_amount}, Location: {customer_location} to database.",
                )

            else:
                missing_feilds = [x for x, y in inputs.items() if y == ""]

                return (False, f"Feild: {', '.join(missing_feilds)} missing!")

        except Exception as e:
            raise e

    def add_collection(self, date, customer, amount):
        try:
            todays_date = date.strftime("%d/%m/%Y")
            repeat = True

            while repeat:
                date_response = self.collection_sheet.find(
                    query=todays_date, in_column=1
                )
                customer_response = self.collection_sheet.find(query=customer, in_row=1)

                if customer_response == None:

                    self.collection_sheet.update_cell(
                        row=1,
                        col=len(self.collection_sheet.row_values(1)) + 1,
                        value=customer,
                    )

                elif date_response == None:

                    self.collection_sheet.update_cell(
                        row=len(self.collection_sheet.col_values(1)) + 1,
                        col=1,
                        value=todays_date,
                    )

                else:
                    date_location = self.collection_sheet.find(
                        query=todays_date, in_column=1
                    )
                    customer_location = self.collection_sheet.find(
                        query=customer, in_row=1
                    )
                    self.collection_sheet.update_cell(
                        row=date_location.row, col=customer_location.col, value=amount
                    )

                    return f"""
                    Date: {todays_date} \n
                    Daily Amount: {amount} \n
                    Customer Name: {customer} \n
                    """
        except Exception as e:
            raise e

    def send_collection(self, date):
        try:
            names = self.collection_sheet.row_values(1)[1:]
            collection = self.collection_sheet.row_values(
                row=self.collection_sheet.find(query=str(date.strftime("%d/%m/%Y"))).row
            )[1:]
            data = pd.DataFrame(data={"Names": names, date: collection})

            return data
        except Exception as e:
            raise e

