"""
Generates a synthetic banking dataset for the Bank Domain Dashboard project.
Creates: customers.csv, accounts.csv, transactions.csv, loans.csv
Also loads everything into a SQLite database (bank.db) for SQL querying.
"""
import pandas as pd
import numpy as np
import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

N_CUSTOMERS = 500
N_ACCOUNTS = 700
N_TRANSACTIONS = 15000
N_LOANS = 250

REGIONS = ["North", "South", "East", "West", "Central"]
ACCOUNT_TYPES = ["Savings", "Checking", "Fixed Deposit"]
LOAN_TYPES = ["Home Loan", "Auto Loan", "Personal Loan", "Education Loan"]
LOAN_STATUS = ["Active", "Closed", "Defaulted"]
TXN_TYPES = ["Deposit", "Withdrawal", "Transfer", "Bill Payment", "POS Purchase"]

# ---------- Customers ----------
customers = []
for i in range(1, N_CUSTOMERS + 1):
    customers.append({
        "customer_id": i,
        "name": fake.name(),
        "gender": random.choice(["Male", "Female"]),
        "age": random.randint(18, 75),
        "region": random.choice(REGIONS),
        "join_date": fake.date_between(start_date="-6y", end_date="-1y"),
        "credit_score": random.randint(300, 850),
    })
customers_df = pd.DataFrame(customers)

# ---------- Accounts ----------
accounts = []
for i in range(1, N_ACCOUNTS + 1):
    cust_id = random.randint(1, N_CUSTOMERS)
    acc_type = random.choice(ACCOUNT_TYPES)
    balance = round(np.random.gamma(shape=2.0, scale=15000), 2)
    accounts.append({
        "account_id": i,
        "customer_id": cust_id,
        "account_type": acc_type,
        "balance": balance,
        "opened_date": fake.date_between(start_date="-6y", end_date="-1y"),
        "status": random.choices(["Active", "Dormant", "Closed"], weights=[0.8, 0.15, 0.05])[0],
    })
accounts_df = pd.DataFrame(accounts)

# ---------- Transactions ----------
transactions = []
start_date = datetime.now() - timedelta(days=365)
for i in range(1, N_TRANSACTIONS + 1):
    acc_id = random.randint(1, N_ACCOUNTS)
    txn_type = random.choice(TXN_TYPES)
    amount = round(np.random.exponential(scale=250), 2) + 1
    txn_date = start_date + timedelta(days=random.randint(0, 365),
                                       hours=random.randint(0, 23),
                                       minutes=random.randint(0, 59))
    # Fraud logic: rare, large, odd-hour transactions are more likely flagged
    is_odd_hour = txn_date.hour < 5 or txn_date.hour > 23
    is_large = amount > 3000
    fraud_prob = 0.002
    if is_large:
        fraud_prob += 0.04
    if is_odd_hour:
        fraud_prob += 0.03
    is_fraud = 1 if random.random() < fraud_prob else 0

    transactions.append({
        "transaction_id": i,
        "account_id": acc_id,
        "transaction_type": txn_type,
        "amount": amount,
        "transaction_date": txn_date.strftime("%Y-%m-%d %H:%M:%S"),
        "is_fraud": is_fraud,
    })
transactions_df = pd.DataFrame(transactions)

# ---------- Loans ----------
loans = []
for i in range(1, N_LOANS + 1):
    cust_id = random.randint(1, N_CUSTOMERS)
    loan_type = random.choice(LOAN_TYPES)
    principal = round(np.random.gamma(shape=2.5, scale=20000), 2)
    interest_rate = round(random.uniform(4.5, 14.0), 2)
    status = random.choices(LOAN_STATUS, weights=[0.65, 0.25, 0.10])[0]
    loans.append({
        "loan_id": i,
        "customer_id": cust_id,
        "loan_type": loan_type,
        "principal_amount": principal,
        "interest_rate": interest_rate,
        "issue_date": fake.date_between(start_date="-5y", end_date="-6m"),
        "status": status,
    })
loans_df = pd.DataFrame(loans)

# ---------- Save CSVs ----------
customers_df.to_csv("data/customers.csv", index=False)
accounts_df.to_csv("data/accounts.csv", index=False)
transactions_df.to_csv("data/transactions.csv", index=False)
loans_df.to_csv("data/loans.csv", index=False)

# ---------- Load into SQLite ----------
conn = sqlite3.connect("data/bank.db")
customers_df.to_sql("customers", conn, if_exists="replace", index=False)
accounts_df.to_sql("accounts", conn, if_exists="replace", index=False)
transactions_df.to_sql("transactions", conn, if_exists="replace", index=False)
loans_df.to_sql("loans", conn, if_exists="replace", index=False)
conn.close()

print("Data generated:")
print(f"  customers.csv     - {len(customers_df)} rows")
print(f"  accounts.csv      - {len(accounts_df)} rows")
print(f"  transactions.csv  - {len(transactions_df)} rows")
print(f"  loans.csv         - {len(loans_df)} rows")
print(f"  Fraud transactions: {transactions_df['is_fraud'].sum()}")
print("SQLite database saved to data/bank.db")
