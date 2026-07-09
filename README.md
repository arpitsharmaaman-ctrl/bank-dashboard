# 🏦 Bank Domain Dashboard

An interactive dashboard for exploring core banking data: **account balances, loan
portfolios, transaction trends, and fraud indicators.** Built with SQL (SQLite) for
data querying/aggregation and Streamlit + Plotly for the interactive visual layer.

**Live demo:** https://bank-dashboard-rprmslboybsq3d8ty74fxj.streamlit.app
**Repo:** https://github.com/arpitsharmaaman-ctrl/bank-dashboard

## Features
- Filterable KPIs: total customers, total balance, active loans, transaction count, flagged fraud
- Balance breakdown by account type and by customer region
- Loan portfolio breakdown by loan type and status (active/closed/defaulted)
- Monthly transaction volume & value trend
- Fraud indicator panel: flagged transactions by type, top flagged transactions table
- Sidebar filters by region and account type

## Tech Stack
- **Data layer:** Python (Pandas, Faker) → SQLite database
- **Querying:** Raw SQL (`sql/queries.sql`) — balances, loan default rates, fraud rates, etc.
- **Dashboard:** Streamlit + Plotly

> **Note on Power BI:** This resume project was originally scoped for Power BI Desktop.
> Since Power BI Desktop is Windows-only and wasn't available in this environment, the
> dashboard was built with Streamlit/Plotly instead — same querying/analysis skills,
> deployable as a live web link. If you have Power BI installed, you can load
> `data/customers.csv`, `data/accounts.csv`, `data/transactions.csv`, and `data/loans.csv`
> directly into Power BI Desktop and rebuild the same visuals there using the queries in
> `sql/queries.sql` as a guide.

## Project Structure
```
bank-dashboard/
├── app.py                  # Streamlit dashboard
├── requirements.txt
├── data/
│   ├── generate_data.py    # Generates synthetic dataset + bank.db
│   ├── customers.csv
│   ├── accounts.csv
│   ├── transactions.csv
│   ├── loans.csv
│   └── bank.db              # SQLite database
├── sql/
│   └── queries.sql          # SQL queries used for the analysis
└── README.md
```

## Run Locally
```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/bank-dashboard.git
cd bank-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Regenerate the dataset
python data/generate_data.py

# 4. Launch the dashboard
streamlit run app.py
```
The app will open at `http://localhost:8501`.

## Deploy for Free (Streamlit Community Cloud)
1. Push this project to a **public GitHub repo**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select your repo, branch `main`, and set the main file to `app.py`.
4. Click **Deploy**. You'll get a live URL like `https://your-app-name.streamlit.app`.
5. Add that link to this README and to your resume.

## Dataset
The dataset is synthetically generated (`data/generate_data.py`) using Faker and
NumPy distributions to mimic realistic banking patterns — 500 customers, 700 accounts,
15,000 transactions, and 250 loans, with a small percentage of transactions flagged as
fraud based on amount and time-of-day heuristics. No real customer or bank data is used.

## SQL Highlights
See `sql/queries.sql` for the full set. Examples:
- Total balance and average balance grouped by account type
- Loan default rate by loan type
- Monthly transaction volume and value trend
- Top 10 highest-value fraud-flagged transactions joined across transactions → accounts → customers
