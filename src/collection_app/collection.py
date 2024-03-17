import os

import gspread
import pandas as pd
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
collection_sheet = workbook.worksheet("Collection")
customers_sheet = workbook.worksheet("Customers")


class Daily_Collection:
    def __init__(self) -> None:
        self.collection_sheet = collection_sheet
        self.customer_sheet = customers_sheet
        self.customers_file_path = "artifacts/customers/customers.csv"
        self.names_text_file = "artifacts/collection/names.txt"
        self.dates_text_file = "artifacts/collection/dates.txt"

        if not os.path.exists(self.customers_file_path):
            paths = ["artifacts/customers", "artifacts/collection"]
            for path in paths:
                os.makedirs(path, exist_ok=True)
            self.__refresh_data__()

        self.customers_df = pd.read_csv(self.customers_file_path)

        with open(self.names_text_file, "r") as f:
            self.names = list(f.read().split("\n"))

        with open(self.dates_text_file, "r") as f:
            self.dates = list(f.read().split("\n"))

    def __refresh_data__(self):
        customers_sheet = self.customer_sheet.get_values()
        names = []
        amounts = []
        locations = []
        for name, amount, location in customers_sheet[1:]:
            names.append(name)
            amounts.append(amount)
            locations.append(location)

        refreshed_data = {
            customers_sheet[0][0]: names,
            customers_sheet[0][1]: amounts,
            customers_sheet[0][2]: locations,
        }
        refreshed_data = pd.DataFrame(refreshed_data)
        refreshed_data.to_csv(self.customers_file_path, index=False)

        dates = self.collection_sheet.col_values(col=1)[1:]
        customers = self.collection_sheet.row_values(row=1)[1:]

        with open(self.names_text_file, "w") as f:
            new_names = "".join([x + "\n" for x in customers])
            f.write(new_names)

        with open(self.dates_text_file, "w") as f:
            new_dates = "".join([x + "\n" for x in dates])
            f.write(new_dates)

    def refresh_customers(self, refresh_btn: bool):
        if refresh_btn:
            self.__refresh_data__()
            return "Data Refresh Complete."

    def get_customer_names(self):
        return self.customers_df["Customer Name"].tolist()

    def get_daily_amount(self, customer):
        amount = self.customers_df.loc[
            self.customers_df["Customer Name"] == customer, "Daily Collection"
        ]
        return int(amount.iloc[0])

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

                if customer_name not in self.names:
                    self.collection_sheet.update_cell(
                        row=1, col=len(self.names) + 1, value=customer_name
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

            if customer not in self.names:
                self.collection_sheet.update_cell(
                    row=1, col=len(self.names) + 1, value=customer
                )

            if todays_date not in self.dates:
                self.collection_sheet.update_cell(
                    row=len(self.dates) + 1, col=1, value=todays_date
                )
                self.__refresh_data__()
                self.collection_sheet.update_cell(
                    row=len(self.dates) + 1,
                    col=self.names.index(customer) + 2,
                    value=amount,
                )

            else:
                self.collection_sheet.update_cell(
                    row=self.dates.index(todays_date) + 2,
                    col=self.names.index(customer) + 2,
                    value=amount,
                )

            return f"""
            Date: {todays_date} \n
            Daily Amount: {amount} \n
            Customer Name: {customer} \n
            """
        except Exception as e:
            raise e

    def show_collection(self, date):
        try:
            names = self.collection_sheet.row_values(1)[1:]
            amounts = self.collection_sheet.row_values(
                row=self.collection_sheet.find(query=str(date.strftime("%d/%m/%Y"))).row
            )[1:]
            names.append("Total")
            amounts.append(sum([int(x) for x in amounts if x != ""]))
            collection = pd.DataFrame(
                data={"Names": names, date.strftime("%d-%m-%Y"): amounts}
            )

            return collection
        except Exception as e:
            raise e

