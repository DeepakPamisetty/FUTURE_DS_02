# Telecom Customer Churn and Retention Analysis

This repository contains a cleaned and organized customer churn analysis for the telecom churn dataset requested from Kaggle:

https://www.kaggle.com/datasets/andrewmvd/churn-dataset-for-telecom-companies

The Kaggle page and API endpoint for the requested slug returned 404 during rebuild, so the raw CSV included here uses the same widely used Telco Customer Churn table structure from IBM's public sample mirror. The analysis remains aligned with the requested telecom churn business problem and can be rebuilt from `data/raw/telco_customer_churn.csv`.

## Dashboard

- View dashboard: https://htmlpreview.github.io/?https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/outputs/telecom_churn_dashboard.html
- Dashboard file in repository: https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/outputs/telecom_churn_dashboard.html
- GitHub Pages URL, after Pages is enabled: https://deepakpamisetty.github.io/FUTURE_DS_02/

The GitHub Pages URL returns 404 until Pages is enabled for this repository from **Settings > Pages**, using the `master` branch and `/root` folder.

## Outputs

- `outputs/telecom_churn_dashboard.html` - client-ready dashboard with KPI cards, SVG charts, segment tables, insights, and recommendations.
- `outputs/charts/*.svg` - lightweight chart assets used by the dashboard.
- `data/processed/telco_churn_cleaned.csv` - cleaned customer-level churn dataset.
- `data/processed/contract_churn.csv` - churn rate, tenure, charge, and revenue-risk metrics by contract type.
- `data/processed/internet_service_churn.csv` - churn metrics by internet service.
- `data/processed/payment_method_churn.csv` - churn metrics by payment method.
- `data/processed/tenure_churn.csv` - churn metrics by tenure bucket.
- `data/processed/monthly_charges_churn.csv` - churn metrics by monthly charge bucket.
- `data/processed/protection_churn.csv` - churn metrics for customers with security/support/device protection services.
- `data/processed/retention_curve.csv` - active customer share by tenure month.
- `data/processed/analysis_summary.json` - summary KPIs and segment metrics used by the dashboard.

## Key Insights

- Overall customer churn is 26.5%, with churned customers representing 30.5% of monthly recurring charges.
- Month-to-month contracts are the highest-risk segment and churn far more than one-year and two-year contracts.
- Fiber optic customers show elevated churn compared with DSL and no-internet-service customers.
- Electronic check users churn at a higher rate than customers using automatic payment methods.
- Early-tenure customers are the most fragile; retention improves strongly as customers move into longer tenure bands.

## Recommendations

- Convert high-risk month-to-month customers into annual plans using loyalty discounts, pause options, and renewal incentives.
- Investigate fiber optic churn drivers through support tickets, pricing perception, and service reliability analysis.
- Encourage electronic-check customers to move to automatic payment methods and add payment recovery reminders.
- Build first-year lifecycle campaigns that focus on onboarding, service education, and proactive support.

## Rebuild

The project uses only the Python standard library.

```bash
python3 scripts/build_telecom_churn_report.py
```

## Repository Structure

```text
FUTURE_DS_02/
├── data/
│   ├── raw/
│   │   └── telco_customer_churn.csv
│   └── processed/
│       ├── analysis_summary.json
│       ├── contract_churn.csv
│       ├── internet_service_churn.csv
│       ├── monthly_charges_churn.csv
│       ├── payment_method_churn.csv
│       ├── protection_churn.csv
│       ├── retention_curve.csv
│       ├── telco_churn_cleaned.csv
│       └── tenure_churn.csv
├── outputs/
│   ├── charts/
│   │   ├── contract_churn.svg
│   │   ├── internet_service_churn.svg
│   │   ├── payment_method_churn.svg
│   │   ├── retention_curve.svg
│   │   └── tenure_churn.svg
│   └── telecom_churn_dashboard.html
├── scripts/
│   └── build_telecom_churn_report.py
├── index.html
└── README.md
```
