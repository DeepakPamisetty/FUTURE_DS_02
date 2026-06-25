# FUTURE_DS_02 - SaaS Customer Churn and Retention Dashboard

This project analyzes customer subscription behavior for a simulated B2B SaaS company. It is designed as a stakeholder-ready retention analysis deliverable for product, growth, and founder teams.

## Dashboard

Open the dashboard:

- `index.html`
- `outputs/retention_dashboard.html`

The dashboard covers:

- Churn rate and revenue churn
- Retention cohorts by signup month
- Churn segmentation by plan, region, and acquisition channel
- Customer lifetime and churn timing
- Churn reasons and practical retention recommendations

## Key Business Findings

- Logo churn is concentrated in lower-activation accounts, especially customers with weak onboarding and low weekly product usage.
- Starter customers have the highest churn risk because they connect fewer integrations and complete onboarding less often.
- Low product usage, price sensitivity, and payment failures are the strongest churn signals in the dataset.
- Business and Enterprise customers retain better because they show higher onboarding completion, deeper integration usage, and longer observed tenure.

## Recommendations

- Create a first-14-day activation sprint focused on onboarding completion and integration setup.
- Add weekly usage-risk alerts for customers below two active days per week.
- Use targeted upgrade prompts for highly active Starter customers before they become price-sensitive churn risks.
- Improve payment recovery with smart retries, card-expiry reminders, and grace periods for high-value accounts.

## Project Structure

```text
FUTURE_DS_02/
├── data/
│   ├── raw/saas_subscription_customers.csv
│   └── processed/
│       ├── analysis_summary.json
│       ├── cohort_retention.json
│       ├── segment_channel.csv
│       ├── segment_plan.csv
│       └── segment_region.csv
├── outputs/retention_dashboard.html
├── scripts/build_retention_dashboard.py
├── index.html
└── README.md
```

## Rebuild

The project uses only the Python standard library.

```bash
python3 scripts/build_retention_dashboard.py
```

## Dataset Note

The dataset is simulated and anonymized to reflect a realistic SaaS subscription retention scenario. It includes customer plan, signup cohort, region, channel, MRR, onboarding status, integrations, product usage, support tickets, payment failures, CSAT, churn status, churn timing, and churn reason.
