import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from uploader import df, workflow

if workflow == 'editor':
    from lang_model_api import gpt_master_config, gpt_a_config, gpt_b_config, gpt_c_config, gpt_d_config, editor_account
else:
    pass

organization_name = 'mlti'
deal_name = input("Deal Name: ")

df['organization'] = organization_name
df['deal'] = deal_name

inc_grwth_rate = .03
exp_grwth_rate = .03
pf_len = 60

class DatabaseManager:

    def __init__(self, db_name):
        """Initialize the DatabaseManager with a database name."""
        self.db_name = db_name

    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connection to database '{self.db_name}' successful")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def query_data(self, query):
        """Query data from the table."""
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Error querying data: {e}")

    def update_data(self, query):
        """Update data in the table."""
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print("Data updated successfully")
        except sqlite3.Error as e:
            print(f"Error updating data: {e}")

    def close_connection(self):
        """Close the connection to the database."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing connection: {e}")

account_import_chart = []
account_type_import_chart = []
account_import_configuration = []
master_config_import_configuration = []
a_config_import_configuration = []
b_config_import_configuration = []
c_config_import_configuration = []
d_config_import_configuration = []
t12_dict_import_historicals = []

db = DatabaseManager("mlti_database.db")
db.connect()

# DATA UPDATES

# Account query from chart_of_accounts
results0 = db.query_data("SELECT account FROM chart_of_accounts")
populator_chart = [result[0] for result in results0]

if workflow == 'populator':
    df.to_sql('historicals', db.conn, if_exists='append', index=False)

    for i in populator_chart:
        db.update_data(f"INSERT INTO configuration (account, organization, deal, master_config, a_config, b_config, c_config, d_config) VALUES ('{i}', '{organization_name}', '{deal_name}', 'value_basic', 't12_avg', 0, 0, 0);")

elif workflow == 'editor':
    db.update_data(f"UPDATE configuration SET master_config = '{gpt_master_config}' WHERE organization = '{organization_name}' AND deal = '{deal_name}' AND account = '{editor_account}'")
    db.update_data(f"UPDATE configuration SET a_config = '{gpt_a_config}' WHERE organization = '{organization_name}' AND deal = '{deal_name}' AND account = '{editor_account}'")
    db.update_data(f"UPDATE configuration SET b_config = '{gpt_b_config}' WHERE organization = '{organization_name}' AND deal = '{deal_name}' AND account = '{editor_account}'")
    db.update_data(f"UPDATE configuration SET c_config = '{gpt_c_config}' WHERE organization = '{organization_name}' AND deal = '{deal_name}' AND account = '{editor_account}'")
    db.update_data(f"UPDATE configuration SET d_config = '{gpt_d_config}' WHERE organization = '{organization_name}' AND deal = '{deal_name}' AND account = '{editor_account}'")

# QUERIES

# Account query from chart_of_accounts
results1 = db.query_data("SELECT account FROM chart_of_accounts;")
account_import_chart = [result[0] for result in results1]

# Account query from pro_forma_chart
results1 = db.query_data("SELECT account FROM pro_forma_chart;")
account_import_pf_chart = [result[0] for result in results1]

# Account type query from chart_of_accounts
results2 = db.query_data("SELECT account_type FROM chart_of_accounts;")
account_type_import_chart = [result[0] for result in results2]

# Account query from configuration
results3 = db.query_data(f"SELECT account FROM configuration WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
account_import_configuration = [result[0] for result in results3]

# master_config query from configuration
results4 = db.query_data(f"SELECT master_config FROM configuration WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
master_config_import_configuration = [result[0] for result in results4]

# a_config query from configuration
results5 = db.query_data(f"SELECT a_config FROM configuration WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
a_config_import_configuration = [result[0] for result in results5]

# b_config query from configuration
results6 = db.query_data(f"SELECT b_config FROM configuration WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
b_config_import_configuration = [result[0] for result in results6]

# c_config query from configuration
results7 = db.query_data(f"SELECT c_config FROM configuration WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
c_config_import_configuration = [result[0] for result in results7]

# d_config query from configuration
results8 = db.query_data(f"SELECT d_config FROM configuration WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
d_config_import_configuration = [result[0] for result in results8]

# t12_dict query from historicals
results9 = db.query_data(f"SELECT account, t12, t11, t10, t9, t8, t7, t6, t5, t4, t3, t2, t1 FROM historicals WHERE organization = '{organization_name}' AND deal = '{deal_name}';")
t12_dict_import_historicals = {row[0]: row[1:] for row in results9}

db.close_connection()

