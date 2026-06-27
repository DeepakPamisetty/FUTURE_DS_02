# Power BI Report Layout

Build a one-page Power BI report named **Telecom Churn Retention Dashboard**.

## Data

Import:

- `data/processed/telco_churn_cleaned.csv`

Rename the table to:

- `TelcoChurn`

Apply:

- `powerbi/power_query_transform.m` for data types
- `powerbi/theme_telecom_retention.json` as the report theme
- `powerbi/measures.dax` as report measures

## Page Setup

- Canvas: 16:9 widescreen
- Background: `#f7f4ee`
- Main visual background: `#fffdf8`
- Accent colors: teal `#168474`, coral `#df6c4f`, gold `#c89b35`

## Header

Add a text box:

**Retention risk is highest in flexible, early-tenure accounts**

Subtitle:

Telecom customer churn dashboard built from contract, tenure, service, payment, and billing behavior.

## KPI Cards

Add six cards across the top:

1. `Customers`
2. `Logo Churn Rate`
3. `Revenue Churn Rate`
4. `Lost Monthly Revenue`
5. `Average Tenure`
6. `Contract Risk Gap`

Format churn and gap measures as percentages. Format revenue measures as currency.

## Slicers

Add slicers on the left or top:

- `Contract`
- `InternetService`
- `PaymentMethod`
- `TenureBucket`
- `MonthlyChargeBucket`
- `HasProtection`

Use dropdown style for compact layout.

## Visuals

### Contract Risk

Clustered bar chart:

- Axis: `Contract`
- Values: `Logo Churn Rate`
- Sort descending by `Logo Churn Rate`

### Internet Service Risk

Clustered bar chart:

- Axis: `InternetService`
- Values: `Logo Churn Rate`
- Sort descending by `Logo Churn Rate`

### Payment Method Risk

Clustered bar chart:

- Axis: `PaymentMethod`
- Values: `Logo Churn Rate`
- Sort descending by `Logo Churn Rate`

### Tenure Pattern

Clustered bar chart:

- Axis: `TenureBucket`
- Values: `Logo Churn Rate`
- Sort by natural tenure order:
  - `0-6 months`
  - `7-12 months`
  - `13-24 months`
  - `25-48 months`
  - `49+ months`

### Revenue at Risk

Treemap or bar chart:

- Group: `Contract`
- Values: `Lost Monthly Revenue`

### Segment Detail Table

Table:

- `Contract`
- `Customers`
- `Churned Customers`
- `Logo Churn Rate`
- `Average Tenure`
- `Average Monthly Charge`
- `Lost Monthly Revenue`

## Insight Cards

Add four text cards:

- Month-to-month contracts are the highest-risk segment.
- Fiber optic customers churn more than DSL and no-internet-service customers.
- Electronic check users show elevated churn compared with automatic payment methods.
- Early-tenure customers are the most fragile, so the first year needs proactive retention programs.

## Recommendations

Add four recommendation cards:

1. Convert high-risk month-to-month customers to annual plans using loyalty discounts and renewal incentives.
2. Investigate fiber optic churn drivers through service quality, support tickets, and pricing perception.
3. Encourage electronic-check customers to move to automatic payment methods.
4. Build first-year lifecycle campaigns focused on onboarding, education, and proactive support.
