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
auth_sheet = workbook.worksheet("Auth")


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
            new_names = "".join([f"{x}\n" for x in customers])
            f.write(new_names)

        with open(self.dates_text_file, "w") as f:
            new_dates = "".join([f"{x}\n" for x in dates])
            f.write(new_dates)

    def get_customer_names(self):
        return self.customers_df["Customer Name"].tolist()

    def get_daily_amount(self, customer):
        amount = self.customers_df.loc[
            self.customers_df["Customer Name"] == customer, "Daily Collection"
        ]
        return int(amount.iloc[0])

    def get_location(self, customer):
        location = self.customers_df.loc[
            self.customers_df["Customer Name"] == customer, "Location"
        ]
        return location.iloc[0]

    def get_name(self, customer):
        name = self.customers_df.loc[
            self.customers_df["Customer Name"] == customer, "Customer Name"
        ]
        return name.iloc[0]

    def get_auth(self, user, pswd):
        self.auth_sheet = auth_sheet

        usrs = self.auth_sheet.col_values(col=1)
        pswds = self.auth_sheet.col_values(col=2)

        # return usrs, pswds

        if user in usrs and pswd in pswds and (usrs.index(user) == pswds.index(pswd)):
            return True
        else:
            return False

    def add_customer(
        self,
        inputs: dict,
        customer_name: str,
        daily_amount: int,
        customer_location: str,
    ):
        try:
            customers_name = self.customer_sheet.col_values(1)[1:]
            if customer_name in customers_name:
                return (True, f"Customer: {customer_name} already exists in database.")

            elif ("" not in inputs.values()) and (customer_name not in customers_name):
                self.customer_sheet.append_row(
                    values=[customer_name, daily_amount, customer_location]
                )

                self.collection_sheet.update_cell(
                    row=1, col=len(self.names) + 1, value=customer_name
                )

                self.__refresh_data__()

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
            date = date.strftime("%m/%d/%Y")

            if date not in self.dates:
                self.collection_sheet.update_cell(
                    row=len(self.dates) + 1, col=1, value=date
                )
                self.__refresh_data__()
                self.dates.append(date)
                self.collection_sheet.update_cell(
                    row=self.dates.index(date) + 1,
                    col=self.names.index(customer) + 2,
                    value=amount,
                )
                # print(self.dates)
            else:
                self.collection_sheet.update_cell(
                    row=self.dates.index(date) + 2,
                    col=self.names.index(customer) + 2,
                    value=amount,
                )
                # print(self.dates)

            return f"""
            Date: {date} \n
            Daily Amount: {amount} \n
            Customer Name: {customer} \n
            """
        except Exception as e:
            raise e

    def show_collection(self, date):
        try:
            date = date.strftime("%m/%d/%Y")
            all_values = self.collection_sheet.get_values()
            customer_names = all_values[0][1:]
            collection = []

            if date in self.dates:
                collection_values = all_values[self.dates.index(date) + 1][1:]
                collection_values = [
                    int(x) if x != "" else 0 for x in collection_values
                ]
                collection.extend(collection_values)
                collection.append(sum(collection_values))
                customer_names.append("Total")

                todays_df = pd.DataFrame(
                    data={"Customer Names": customer_names, date: collection}
                )

                return todays_df.sort_values(
                    by=[date, "Customer Names"], ascending=False, ignore_index=True
                )

            else:
                return f"No data found for date: {date}"

        except Exception as e:
            raise e

    def update_customer(self, customer, name, customer_collection, location):

        cust_details = self.customers_df.loc[
            self.customers_df["Customer Name"] == customer
        ].values.tolist()

        cust_detail_list = [name, customer_collection, location]

        if cust_details[0] == cust_detail_list:
            return "No changes to be done"
        else:
            idx = self.customers_df["Customer Name"].values.tolist().index(customer)

            res = ""

            for each in range(len(cust_detail_list)):

                if cust_detail_list[each] not in cust_details[0]:
                    res += f"Changed values for {customer} from {cust_details[0][each]} to {cust_detail_list[each]}\n"

                    self.customer_sheet.update_cell(
                        row=idx + 2, col=each + 1, value=cust_detail_list[each]
                    )

                    if customer != name:
                        self.collection_sheet.update_cell(
                            row=1, col=idx + 2, value=name
                        )

            self.__refresh_data__()

            return res
