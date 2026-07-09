"""
Bank Domain Dashboard
Interactive dashboard built with Streamlit + Plotly + SQLite/SQL.
Shows account balances, loan portfolio, transaction trends, and fraud indicators.
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Bank Domain Dashboard", layout="wide", page_icon="🏦")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bank.db")


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    customers = pd.read_sql("SELECT * FROM customers", conn)
    accounts = pd.read_sql("SELECT * FROM accounts", conn)
    transactions = pd.read_sql("SELECT * FROM transactions", conn)
    loans = pd.read_sql("SELECT * FROM loans", conn)
    conn.close()
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
    return customers, accounts, transactions, loans


customers, accounts, transactions, loans = load_data()

# ---------------- Sidebar filters ----------------
st.sidebar.title("🏦 Bank Dashboard")
st.sidebar.markdown("Filter the data below:")

regions = st.sidebar.multiselect("Region", options=sorted(customers["region"].unique()),
                                  default=sorted(customers["region"].unique()))
acc_types = st.sidebar.multiselect("Account Type", options=sorted(accounts["account_type"].unique()),
                                    default=sorted(accounts["account_type"].unique()))

filtered_customers = customers[customers["region"].isin(regions)]
filtered_accounts = accounts[
    accounts["customer_id"].isin(filtered_customers["customer_id"]) &
    accounts["account_type"].isin(acc_types)
]
filtered_txns = transactions[transactions["account_id"].isin(filtered_accounts["account_id"])]
filtered_loans = loans[loans["customer_id"].isin(filtered_customers["customer_id"])]

# ---------------- Header KPIs ----------------
st.title("Bank Domain Dashboard")
st.caption("Balances · Loans · Transactions · Fraud Indicators — powered by SQL + Python")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Customers", f"{filtered_customers['customer_id'].nunique():,}")
col2.metric("Total Balance", f"${filtered_accounts['balance'].sum():,.0f}")
col3.metric("Active Loans", f"{(filtered_loans['status'] == 'Active').sum():,}")
col4.metric("Transactions", f"{len(filtered_txns):,}")
fraud_count = int(filtered_txns["is_fraud"].sum())
col5.metric("Flagged Fraud", f"{fraud_count:,}", delta=f"{fraud_count/len(filtered_txns)*100:.2f}%" if len(filtered_txns) else "0%",
            delta_color="inverse")

st.divider()

# ---------------- Row 1: Balances ----------------
c1, c2 = st.columns(2)
with c1:
    st.subheader("Balance by Account Type")
    bal_by_type = filtered_accounts.groupby("account_type")["balance"].sum().reset_index()
    fig = px.bar(bal_by_type, x="account_type", y="balance", color="account_type",
                 text_auto=".2s", title=None)
    fig.update_layout(showlegend=False, yaxis_title="Total Balance ($)", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Balance by Region")
    reg_bal = filtered_accounts.merge(customers[["customer_id", "region"]], on="customer_id")
    reg_bal = reg_bal.groupby("region")["balance"].sum().reset_index()
    fig = px.pie(reg_bal, names="region", values="balance", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 2: Loans ----------------
c3, c4 = st.columns(2)
with c3:
    st.subheader("Loan Portfolio by Type")
    loan_by_type = filtered_loans.groupby("loan_type")["principal_amount"].sum().reset_index()
    fig = px.bar(loan_by_type, x="loan_type", y="principal_amount", color="loan_type", text_auto=".2s")
    fig.update_layout(showlegend=False, yaxis_title="Principal Amount ($)", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Loan Status Breakdown")
    status_counts = filtered_loans["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(status_counts, names="status", values="count", hole=0.45,
                 color="status", color_discrete_map={"Active": "#2E86AB", "Closed": "#8AB17D", "Defaulted": "#E63946"})
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 3: Transactions over time ----------------
st.subheader("Monthly Transaction Volume & Value")
monthly = filtered_txns.copy()
monthly["month"] = monthly["transaction_date"].dt.to_period("M").astype(str)
monthly_agg = monthly.groupby("month").agg(num_transactions=("transaction_id", "count"),
                                            total_value=("amount", "sum")).reset_index()
fig = go.Figure()
fig.add_trace(go.Bar(x=monthly_agg["month"], y=monthly_agg["total_value"], name="Total Value ($)", yaxis="y1"))
fig.add_trace(go.Scatter(x=monthly_agg["month"], y=monthly_agg["num_transactions"], name="Num Transactions",
                          yaxis="y2", mode="lines+markers", line=dict(color="orange")))
fig.update_layout(
    yaxis=dict(title="Total Value ($)"),
    yaxis2=dict(title="Num Transactions", overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 4: Fraud indicators ----------------
st.subheader("🚩 Fraud Indicators")
fraud_txns = filtered_txns[filtered_txns["is_fraud"] == 1].merge(
    accounts[["account_id", "account_type", "customer_id"]], on="account_id"
).merge(customers[["customer_id", "name", "region"]], on="customer_id")

fc1, fc2 = st.columns([1, 2])
with fc1:
    st.metric("Total Flagged Transactions", len(fraud_txns))
    st.metric("Total Flagged Value", f"${fraud_txns['amount'].sum():,.0f}")
    by_type = fraud_txns["transaction_type"].value_counts().reset_index()
    by_type.columns = ["type", "count"]
    fig = px.bar(by_type, x="type", y="count", title="Fraud Flags by Transaction Type")
    st.plotly_chart(fig, use_container_width=True)

with fc2:
    st.markdown("**Top flagged transactions**")
    top_fraud = fraud_txns.sort_values("amount", ascending=False)[
        ["transaction_id", "transaction_date", "transaction_type", "amount", "name", "region"]
    ].head(15)
    st.dataframe(top_fraud, use_container_width=True, hide_index=True)

st.divider()
st.caption("Built with Python, SQL (SQLite), Streamlit & Plotly · Synthetic data for demo purposes.")
