#!/usr/bin/env python3
"""Build a SaaS churn and retention dashboard from simulated subscription data."""

from __future__ import annotations

import csv
import html
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "saas_subscription_customers.csv"
PROCESSED = ROOT / "data" / "processed"
DASHBOARD = ROOT / "outputs" / "retention_dashboard.html"
INDEX = ROOT / "index.html"
ANALYSIS_DATE = date(2026, 6, 1)


PLANS = {
    "Starter": 29,
    "Growth": 79,
    "Business": 149,
    "Enterprise": 399,
}
REGIONS = ["North America", "Europe", "APAC", "LATAM", "MEA"]
CHANNELS = ["Organic", "Paid Search", "Partner", "Referral", "Content"]
INDUSTRIES = ["EdTech", "FinTech", "Healthcare", "Creator Tools", "Retail", "B2B SaaS"]
CHURN_REASONS = [
    "Low product usage",
    "Price sensitivity",
    "Missing integration",
    "Switched competitor",
    "Payment failure",
    "Poor onboarding",
    "Company downsized",
]


def month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def add_months(d: date, months: int) -> date:
    total = d.year * 12 + d.month - 1 + months
    return date(total // 12, total % 12 + 1, 1)


def month_diff(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def money(value: float) -> str:
    return f"${value:,.0f}"


def bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def choose_weighted(items: list[str], weights: list[float]) -> str:
    return random.choices(items, weights=weights, k=1)[0]


def generate_dataset() -> list[dict[str, str]]:
    random.seed(42)
    rows: list[dict[str, str]] = []
    signup_months = [add_months(date(2025, 1, 1), i) for i in range(15)]
    plan_names = list(PLANS)

    for idx in range(1, 1401):
        signup_month = choose_weighted(
            [m.isoformat() for m in signup_months],
            [0.70 + i * 0.045 for i in range(len(signup_months))],
        )
        signup_date = date.fromisoformat(signup_month) + timedelta(days=random.randint(0, 27))
        plan = choose_weighted(plan_names, [0.42, 0.32, 0.18, 0.08])
        region = choose_weighted(REGIONS, [0.36, 0.26, 0.22, 0.10, 0.06])
        channel = choose_weighted(CHANNELS, [0.33, 0.22, 0.18, 0.17, 0.10])
        industry = random.choice(INDUSTRIES)

        onboarding = random.random() < {
            "Starter": 0.58,
            "Growth": 0.70,
            "Business": 0.78,
            "Enterprise": 0.88,
        }[plan]
        integrations = max(0, int(random.gauss({"Starter": 1.0, "Growth": 2.0, "Business": 3.0, "Enterprise": 5.0}[plan], 1.2)))
        weekly_active_days = bounded(
            random.gauss(2.2 + integrations * 0.45 + (1.0 if onboarding else -0.6), 1.1),
            0,
            7,
        )
        support_tickets = max(0, int(random.gauss(1.1 + (0.9 if not onboarding else 0) + random.random() * 1.2, 1.1)))
        payment_failures = random.choices([0, 1, 2, 3], weights=[0.78, 0.15, 0.05, 0.02], k=1)[0]
        csat = bounded(
            random.gauss(7.2 + weekly_active_days * 0.28 + integrations * 0.12 - support_tickets * 0.38, 1.1),
            1,
            10,
        )

        churn_risk = 0.08
        churn_risk += {"Starter": 0.09, "Growth": 0.04, "Business": 0.015, "Enterprise": -0.025}[plan]
        churn_risk += 0.13 if weekly_active_days < 2 else -0.05 if weekly_active_days >= 5 else 0
        churn_risk += 0.10 if not onboarding else -0.035
        churn_risk += min(0.16, payment_failures * 0.065)
        churn_risk += 0.04 if support_tickets >= 4 else 0
        churn_risk += -0.055 if integrations >= 3 else 0.04 if integrations == 0 else 0
        churn_risk += {"Referral": -0.03, "Partner": -0.02, "Paid Search": 0.035}.get(channel, 0)
        churn_risk += {"LATAM": 0.025, "MEA": 0.035, "North America": -0.01}.get(region, 0)
        churn_risk = bounded(churn_risk, 0.035, 0.58)

        age_months = max(0, month_diff(month_start(signup_date), ANALYSIS_DATE))
        churned = random.random() < churn_risk and age_months >= 1
        churn_month = ""
        churn_reason = ""
        tenure_months = age_months + 1
        status = "Active"

        if churned:
            early_bias = 1.9 if not onboarding or weekly_active_days < 2 else 1.2
            churn_after = max(1, min(age_months, int(random.betavariate(1.3, early_bias) * age_months) + 1))
            churn_month_date = add_months(month_start(signup_date), churn_after)
            churn_month = churn_month_date.isoformat()
            tenure_months = churn_after
            status = "Churned"
            reason_weights = [
                0.25 if weekly_active_days < 2 else 0.11,
                0.20 if plan == "Starter" else 0.10,
                0.18 if integrations <= 1 else 0.08,
                0.13,
                0.22 if payment_failures else 0.05,
                0.20 if not onboarding else 0.07,
                0.08,
            ]
            churn_reason = choose_weighted(CHURN_REASONS, reason_weights)

        discount = random.choice([0, 0, 0, 5, 10, 15, 20])
        mrr = PLANS[plan] * (1 - discount / 100) * random.uniform(0.92, 1.18)
        seats = max(1, int(random.gauss({"Starter": 2, "Growth": 6, "Business": 18, "Enterprise": 70}[plan], 3)))

        rows.append(
            {
                "customer_id": f"CUST-{idx:04d}",
                "signup_date": signup_date.isoformat(),
                "signup_month": month_start(signup_date).isoformat(),
                "plan": plan,
                "region": region,
                "acquisition_channel": channel,
                "industry": industry,
                "seats": str(seats),
                "monthly_mrr": f"{mrr:.2f}",
                "onboarding_completed": "Yes" if onboarding else "No",
                "integrations_connected": str(integrations),
                "weekly_active_days": f"{weekly_active_days:.1f}",
                "support_tickets_90d": str(support_tickets),
                "payment_failures_90d": str(payment_failures),
                "csat_score": f"{csat:.1f}",
                "status": status,
                "churn_month": churn_month,
                "churn_reason": churn_reason,
                "tenure_months": str(tenure_months),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_rows() -> list[dict[str, str]]:
    if not RAW.exists():
        rows = generate_dataset()
        write_csv(RAW, rows)
    with RAW.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def segment(rows: list[dict[str, str]], field: str) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    output = []
    for name, items in grouped.items():
        churned = [r for r in items if r["status"] == "Churned"]
        active = [r for r in items if r["status"] == "Active"]
        output.append(
            {
                "segment": name,
                "customers": len(items),
                "churn_rate": len(churned) / len(items),
                "avg_tenure": sum(int(r["tenure_months"]) for r in items) / len(items),
                "active_mrr": sum(float(r["monthly_mrr"]) for r in active),
                "lost_mrr": sum(float(r["monthly_mrr"]) for r in churned),
                "avg_usage": sum(float(r["weekly_active_days"]) for r in items) / len(items),
                "onboarding_rate": sum(r["onboarding_completed"] == "Yes" for r in items) / len(items),
            }
        )
    return sorted(output, key=lambda x: (-float(x["churn_rate"]), str(x["segment"])))


def cohort_table(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["signup_month"]].append(row)

    table = []
    for month in sorted(grouped):
        cohort = grouped[month]
        start = date.fromisoformat(month)
        max_age = month_diff(start, ANALYSIS_DATE)
        values = []
        for age in range(0, min(max_age, 12) + 1):
            retained = 0
            for row in cohort:
                churn_month = row["churn_month"]
                retained += not churn_month or month_diff(start, date.fromisoformat(churn_month)) > age
            values.append(retained / len(cohort))
        table.append({"cohort": month[:7], "customers": len(cohort), "retention": values})
    return table


def analyze(rows: list[dict[str, str]]) -> dict[str, object]:
    total = len(rows)
    churned = [r for r in rows if r["status"] == "Churned"]
    active = [r for r in rows if r["status"] == "Active"]
    active_mrr = sum(float(r["monthly_mrr"]) for r in active)
    lost_mrr = sum(float(r["monthly_mrr"]) for r in churned)
    onboarded = [r for r in rows if r["onboarding_completed"] == "Yes"]
    not_onboarded = [r for r in rows if r["onboarding_completed"] == "No"]
    high_usage = [r for r in rows if float(r["weekly_active_days"]) >= 4]
    low_usage = [r for r in rows if float(r["weekly_active_days"]) < 2]
    reason_counts = Counter(r["churn_reason"] for r in churned if r["churn_reason"])

    def churn_rate(items: list[dict[str, str]]) -> float:
        return sum(r["status"] == "Churned" for r in items) / len(items) if items else 0

    tenure_buckets = Counter()
    for row in churned:
        tenure = int(row["tenure_months"])
        if tenure <= 1:
            tenure_buckets["0-1 mo"] += 1
        elif tenure <= 3:
            tenure_buckets["2-3 mo"] += 1
        elif tenure <= 6:
            tenure_buckets["4-6 mo"] += 1
        elif tenure <= 12:
            tenure_buckets["7-12 mo"] += 1
        else:
            tenure_buckets["12+ mo"] += 1

    return {
        "analysis_date": ANALYSIS_DATE.isoformat(),
        "kpis": {
            "customers": total,
            "active_customers": len(active),
            "logo_churn_rate": len(churned) / total,
            "active_mrr": active_mrr,
            "lost_mrr": lost_mrr,
            "revenue_churn_rate": lost_mrr / (active_mrr + lost_mrr),
            "avg_tenure_months": sum(int(r["tenure_months"]) for r in rows) / total,
            "avg_active_usage_days": sum(float(r["weekly_active_days"]) for r in active) / len(active),
            "onboarding_churn_delta": churn_rate(not_onboarded) - churn_rate(onboarded),
            "usage_churn_delta": churn_rate(low_usage) - churn_rate(high_usage),
        },
        "segments": {
            "plan": segment(rows, "plan"),
            "region": segment(rows, "region"),
            "channel": segment(rows, "acquisition_channel"),
        },
        "cohorts": cohort_table(rows),
        "churn_reasons": [{"reason": k, "customers": v} for k, v in reason_counts.most_common()],
        "tenure_buckets": [{"bucket": k, "customers": tenure_buckets[k]} for k in ["0-1 mo", "2-3 mo", "4-6 mo", "7-12 mo", "12+ mo"]],
    }


def bar_svg(items: list[dict[str, object]], label_key: str, value_key: str, fmt: str = "pct", width: int = 780, height: int = 270) -> str:
    max_value = max(float(item[value_key]) for item in items) or 1
    left, top, row_h = 170, 24, 38
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="bar chart">']
    for i, item in enumerate(items):
        y = top + i * row_h
        value = float(item[value_key])
        bar_w = (width - left - 110) * value / max_value
        label = html.escape(str(item[label_key]))
        display = pct(value) if fmt == "pct" else f"{value:.1f}"
        parts.append(f'<text x="0" y="{y + 18}" class="axis-label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{width-left-110}" height="24" rx="5" class="track"/>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="24" rx="5" class="bar"/>')
        parts.append(f'<text x="{left + bar_w + 10:.1f}" y="{y + 18}" class="value-label">{display}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def simple_count_svg(items: list[dict[str, object]], label_key: str, value_key: str, width: int = 780, height: int = 270) -> str:
    max_value = max(int(item[value_key]) for item in items) or 1
    left, top, row_h = 190, 24, 34
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="count chart">']
    for i, item in enumerate(items):
        y = top + i * row_h
        value = int(item[value_key])
        bar_w = (width - left - 90) * value / max_value
        label = html.escape(str(item[label_key]))
        parts.append(f'<text x="0" y="{y + 17}" class="axis-label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{width-left-90}" height="22" rx="5" class="track"/>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="22" rx="5" class="bar-alt"/>')
        parts.append(f'<text x="{left + bar_w + 10:.1f}" y="{y + 17}" class="value-label">{value}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def heat_color(value: float) -> str:
    # Coral for weak retention, teal for strong retention.
    red = int(235 - value * 122)
    green = int(105 + value * 82)
    blue = int(92 + value * 86)
    return f"rgb({red},{green},{blue})"


def cohort_heatmap(cohorts: list[dict[str, object]]) -> str:
    max_cols = max(len(c["retention"]) for c in cohorts)
    head = "<tr><th>Cohort</th><th>Customers</th>" + "".join(f"<th>M+{i}</th>" for i in range(max_cols)) + "</tr>"
    rows = []
    for cohort in cohorts:
        cells = [f"<td>{cohort['cohort']}</td>", f"<td>{cohort['customers']}</td>"]
        for value in cohort["retention"]:
            cells.append(f'<td style="background:{heat_color(float(value))}">{pct(float(value))}</td>')
        for _ in range(max_cols - len(cohort["retention"])):
            cells.append('<td class="blank">-</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return '<table class="heatmap">' + head + "".join(rows) + "</table>"


def segment_table(items: list[dict[str, object]]) -> str:
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item['segment']))}</td>"
            f"<td>{item['customers']}</td>"
            f"<td>{pct(float(item['churn_rate']))}</td>"
            f"<td>{float(item['avg_tenure']):.1f}</td>"
            f"<td>{pct(float(item['onboarding_rate']))}</td>"
            f"<td>{money(float(item['lost_mrr']))}</td>"
            "</tr>"
        )
    return (
        "<table><tr><th>Segment</th><th>Customers</th><th>Churn</th><th>Avg tenure</th>"
        "<th>Onboarded</th><th>Lost MRR</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def render_dashboard(summary: dict[str, object]) -> str:
    kpis = summary["kpis"]
    plan_segments = summary["segments"]["plan"]
    region_segments = summary["segments"]["region"]
    channel_segments = summary["segments"]["channel"]
    churn_reasons = summary["churn_reasons"]
    tenure = summary["tenure_buckets"]

    cards = [
        ("Logo churn", pct(kpis["logo_churn_rate"]), "Share of customers that cancelled"),
        ("Revenue churn", pct(kpis["revenue_churn_rate"]), "Share of MRR lost to churn"),
        ("Active MRR", money(kpis["active_mrr"]), "Current recurring revenue base"),
        ("Avg tenure", f"{kpis['avg_tenure_months']:.1f} mo", "Customer lifetime observed"),
        ("Usage gap", f"+{kpis['usage_churn_delta'] * 100:.1f} pts", "Low-usage churn premium"),
        ("Onboarding gap", f"+{kpis['onboarding_churn_delta'] * 100:.1f} pts", "Non-onboarded churn premium"),
    ]
    card_html = "\n".join(
        f'<section class="kpi"><span>{label}</span><strong>{value}</strong><p>{detail}</p></section>'
        for label, value, detail in cards
    )

    insights = [
        "Starter customers are the riskiest segment; their lower onboarding and integration depth point to early value realization as the main retention lever.",
        "Missing integrations, price sensitivity, and low usage are the top churn themes, which points to a mix of product-fit and activation gaps.",
        "Customers with fewer than two active days per week churn far more often than highly engaged accounts.",
        "Payment failures are a smaller churn reason, but they are operationally addressable and should be handled before involuntary cancellations happen.",
        "Enterprise and Business accounts retain better because they connect more integrations and complete onboarding at higher rates.",
    ]
    insight_html = "".join(f"<li>{html.escape(i)}</li>" for i in insights)

    recommendations = [
        ("First 14-day activation sprint", "Trigger guided onboarding, milestone emails, and CSM outreach until the account connects at least two integrations."),
        ("Usage-risk intervention", "Create a weekly alert for accounts below two active days and route them to lifecycle campaigns before renewal."),
        ("Starter-to-Growth migration", "Bundle high-retention features and usage limits into upgrade prompts for active Starter accounts."),
        ("Payment recovery playbook", "Add pre-expiry card reminders, smart retries, and a temporary grace period for high-value accounts."),
    ]
    rec_html = "".join(f"<article><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></article>" for t, d in recommendations)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FUTURE_DS_02 | SaaS Retention Dashboard</title>
  <style>
    :root {{
      --ink: #16211f;
      --muted: #62706b;
      --paper: #f7f4ee;
      --panel: #fffdf8;
      --line: #ded7ca;
      --teal: #1b8a7a;
      --coral: #e46d52;
      --gold: #c59b36;
      --charcoal: #24302d;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    header {{
      min-height: 360px;
      display: grid;
      align-items: end;
      background:
        linear-gradient(110deg, rgba(22,33,31,.94), rgba(22,33,31,.72)),
        repeating-linear-gradient(135deg, #31413d 0 2px, #283631 2px 12px);
      color: #fffdf8;
      padding: 48px clamp(20px, 5vw, 72px);
    }}
    header p {{ max-width: 760px; color: #d7e1dc; font-size: 1.08rem; }}
    .eyebrow {{ color: #f4c76c; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; font-size: .78rem; }}
    h1 {{ margin: 10px 0 12px; max-width: 900px; font-size: clamp(2.3rem, 6vw, 5.2rem); line-height: .96; letter-spacing: 0; }}
    h2 {{ margin: 0 0 16px; font-size: clamp(1.45rem, 2.5vw, 2.1rem); }}
    h3 {{ margin: 0 0 8px; font-size: 1rem; }}
    main {{ padding: 30px clamp(18px, 4vw, 56px) 56px; }}
    .kpis {{ display: grid; grid-template-columns: repeat(6, minmax(150px, 1fr)); gap: 14px; margin-top: -76px; }}
    .kpi {{
      min-height: 148px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 12px 30px rgba(36,48,45,.08);
    }}
    .kpi span {{ color: var(--muted); font-weight: 800; font-size: .8rem; text-transform: uppercase; }}
    .kpi strong {{ display: block; margin: 10px 0 6px; font-size: clamp(1.55rem, 2.6vw, 2.25rem); color: var(--charcoal); }}
    .kpi p {{ margin: 0; color: var(--muted); font-size: .9rem; }}
    .grid {{ display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr); gap: 22px; margin-top: 24px; }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 22px;
    }}
    .panel.full {{ grid-column: 1 / -1; }}
    .split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
    svg {{ width: 100%; height: auto; }}
    .axis-label {{ fill: #4f5f5a; font-size: 14px; font-weight: 700; }}
    .value-label {{ fill: #1d2a27; font-size: 14px; font-weight: 800; }}
    .track {{ fill: #ebe5da; }}
    .bar {{ fill: var(--coral); }}
    .bar-alt {{ fill: var(--teal); }}
    table {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
    th, td {{ padding: 10px 9px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ color: var(--muted); font-size: .74rem; text-transform: uppercase; letter-spacing: .06em; }}
    .heatmap th, .heatmap td {{ text-align: center; min-width: 64px; color: #13201d; font-weight: 800; }}
    .heatmap td:first-child, .heatmap td:nth-child(2) {{ background: #fffdf8; text-align: left; font-weight: 700; }}
    .heatmap .blank {{ color: #9a9488; background: #eee8dc; }}
    .notes {{ margin: 0; padding-left: 20px; color: var(--charcoal); }}
    .notes li {{ margin-bottom: 10px; }}
    .recommendations {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .recommendations article {{ border-left: 5px solid var(--gold); padding: 6px 12px; background: #fbf6ea; border-radius: 0 8px 8px 0; }}
    .recommendations p {{ margin: 0; color: var(--muted); }}
    footer {{ padding: 0 clamp(18px, 4vw, 56px) 36px; color: var(--muted); }}
    @media (max-width: 1100px) {{
      .kpis {{ grid-template-columns: repeat(3, 1fr); }}
      .grid, .split {{ grid-template-columns: 1fr; }}
      .recommendations {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 680px) {{
      header {{ min-height: 330px; padding: 36px 18px 92px; }}
      .kpis {{ grid-template-columns: 1fr; margin-top: -72px; }}
      .panel {{ padding: 16px; overflow-x: auto; }}
      .recommendations {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <div class="eyebrow">FUTURE_DS_02 · SaaS retention analytics</div>
      <h1>Churn is concentrated in low-activation accounts.</h1>
      <p>Simulated subscription data for a B2B SaaS platform, analyzed as a stakeholder dashboard for product, growth, and founder teams. Analysis date: {summary['analysis_date']}.</p>
    </div>
  </header>
  <main>
    <section class="kpis">{card_html}</section>
    <section class="grid">
      <article class="panel">
        <h2>Churn by Plan</h2>
        {bar_svg(plan_segments, "segment", "churn_rate")}
      </article>
      <article class="panel">
        <h2>What Drives Churn</h2>
        {simple_count_svg(churn_reasons, "reason", "customers")}
      </article>
      <article class="panel full">
        <h2>Monthly Signup Cohort Retention</h2>
        {cohort_heatmap(summary["cohorts"])}
      </article>
      <article class="panel">
        <h2>Regional Risk</h2>
        {segment_table(region_segments)}
      </article>
      <article class="panel">
        <h2>Acquisition Channel Quality</h2>
        {segment_table(channel_segments)}
      </article>
      <article class="panel">
        <h2>Churn Timing</h2>
        {simple_count_svg(tenure, "bucket", "customers")}
      </article>
      <article class="panel">
        <h2>Executive Insights</h2>
        <ul class="notes">{insight_html}</ul>
      </article>
      <article class="panel full">
        <h2>Recommended Retention Actions</h2>
        <div class="recommendations">{rec_html}</div>
      </article>
    </section>
  </main>
  <footer>
    Source: generated SaaS subscription dataset in <code>data/raw/saas_subscription_customers.csv</code>. Rebuild with <code>python3 scripts/build_retention_dashboard.py</code>.
  </footer>
</body>
</html>
"""


def write_outputs(rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for name, items in summary["segments"].items():
        with (PROCESSED / f"segment_{name}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(items[0]))
            writer.writeheader()
            writer.writerows(items)

    with (PROCESSED / "cohort_retention.json").open("w", encoding="utf-8") as f:
        json.dump(summary["cohorts"], f, indent=2)

    dashboard_html = render_dashboard(summary)
    DASHBOARD.write_text(dashboard_html, encoding="utf-8")
    INDEX.write_text(dashboard_html, encoding="utf-8")


def main() -> None:
    rows = read_rows()
    summary = analyze(rows)
    write_outputs(rows, summary)
    print(f"Built dashboard: {DASHBOARD}")
    print(f"Customers: {summary['kpis']['customers']}")
    print(f"Logo churn: {pct(summary['kpis']['logo_churn_rate'])}")


if __name__ == "__main__":
    main()
