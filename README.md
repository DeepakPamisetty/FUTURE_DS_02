# Telecom Customer Churn and Retention Analysis

This repository contains a cleaned and organized customer churn analysis for the telecom churn dataset requested from Kaggle:

https://www.kaggle.com/datasets/andrewmvd/churn-dataset-for-telecom-companies

The Kaggle page and API endpoint for the requested slug returned 404 during rebuild, so the raw CSV included here uses the same widely used Telco Customer Churn table structure from IBM's public sample mirror. The analysis remains aligned with the requested telecom churn business problem and can be rebuilt from `data/raw/telco_customer_churn.csv`.

## Dashboard

- View dashboard: https://htmlpreview.github.io/?https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/outputs/telecom_churn_dashboard.html
- Dashboard file in repository: https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/outputs/telecom_churn_dashboard.html
- GitHub Pages URL, after Pages is enabled: https://deepakpamisetty.github.io/FUTURE_DS_02/
- Power BI build guide: https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/powerbi/report_layout.md
- Power BI Project file: https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/powerbi/FUTURE_DS_02.pbip
- Power BI DAX measures: https://github.com/DeepakPamisetty/FUTURE_DS_02/blob/master/powerbi/measures.dax

The GitHub Pages URL returns 404 until Pages is enabled for this repository from **Settings > Pages**, using the `master` branch and `/root` folder.

## Power BI Version

Power BI Desktop is not available in this Mac workspace, so a `.pbix` binary could not be generated directly here. The repository includes a Power BI Project scaffold and build pack:

- `powerbi/FUTURE_DS_02.pbip` - Power BI Project entry file.
- `powerbi/FUTURE_DS_02.SemanticModel/` - semantic model source with the `TelcoChurn` table and core measures.
- `powerbi/FUTURE_DS_02.Report/` - report project folder connected to the semantic model.
- `powerbi/report_layout.md` - exact dashboard layout for Power BI.
- `powerbi/measures.dax` - DAX measures for churn, retention, and revenue risk.
- `powerbi/power_query_transform.m` - Power Query transformations and data types.
- `powerbi/theme_telecom_retention.json` - Power BI theme matching the dashboard style.

To build the Power BI report, open `powerbi/FUTURE_DS_02.pbip` in Power BI Desktop, refresh the `TelcoChurn` table, apply the theme, and recreate or refine the visuals using `powerbi/report_layout.md`. Then save as `.pbix`.

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
├── powerbi/
│   ├── FUTURE_DS_02.pbip
│   ├── FUTURE_DS_02.Report/
│   │   └── definition.pbir
│   ├── FUTURE_DS_02.SemanticModel/
│   │   ├── definition.pbism
│   │   └── definition/
│   │       ├── model.tmdl
│   │       └── tables/
│   │           └── TelcoChurn.tmdl
│   ├── measures.dax
│   ├── power_query_transform.m
│   ├── report_layout.md
│   └── theme_telecom_retention.json
├── scripts/
│   └── build_telecom_churn_report.py
├── index.html
└── README.md
```
