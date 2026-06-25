#!/usr/bin/env python3
"""Build a telecom churn dashboard from the Telco Customer Churn dataset."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "telco_customer_churn.csv"
PROCESSED = ROOT / "data" / "processed"
CHARTS = ROOT / "outputs" / "charts"
DASHBOARD = ROOT / "outputs" / "telecom_churn_dashboard.html"
INDEX = ROOT / "index.html"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def money(value: float) -> str:
    return f"${value:,.0f}"


def read_rows() -> list[dict[str, object]]:
    if not RAW.exists():
        raise FileNotFoundError(
            f"Missing {RAW}. Download the Kaggle telecom churn CSV and save it at this path."
        )

    cleaned: list[dict[str, object]] = []
    with RAW.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total_charges = row["TotalCharges"].strip()
            if not total_charges:
                total = float(row["MonthlyCharges"])
            else:
                total = float(total_charges)
            cleaned.append(
                {
                    **row,
                    "SeniorCitizen": "Yes" if row["SeniorCitizen"] == "1" else "No",
                    "tenure": int(row["tenure"]),
                    "MonthlyCharges": float(row["MonthlyCharges"]),
                    "TotalCharges": total,
                    "ChurnFlag": 1 if row["Churn"] == "Yes" else 0,
                    "TenureBucket": tenure_bucket(int(row["tenure"])),
                    "MonthlyChargeBucket": charge_bucket(float(row["MonthlyCharges"])),
                    "HasProtection": "Yes"
                    if row["OnlineSecurity"] == "Yes"
                    or row["TechSupport"] == "Yes"
                    or row["DeviceProtection"] == "Yes"
                    else "No",
                }
            )
    return cleaned


def tenure_bucket(tenure: int) -> str:
    if tenure <= 6:
        return "0-6 months"
    if tenure <= 12:
        return "7-12 months"
    if tenure <= 24:
        return "13-24 months"
    if tenure <= 48:
        return "25-48 months"
    return "49+ months"


def charge_bucket(charge: float) -> str:
    if charge < 35:
        return "Under $35"
    if charge < 70:
        return "$35-$69"
    if charge < 95:
        return "$70-$94"
    return "$95+"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize_segment(rows: list[dict[str, object]], field: str) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row)

    output = []
    for segment, items in groups.items():
        churned = [r for r in items if r["ChurnFlag"] == 1]
        output.append(
            {
                "segment": segment,
                "customers": len(items),
                "churned": len(churned),
                "churn_rate": len(churned) / len(items),
                "avg_tenure": sum(float(r["tenure"]) for r in items) / len(items),
                "avg_monthly_charges": sum(float(r["MonthlyCharges"]) for r in items) / len(items),
                "lost_monthly_revenue": sum(float(r["MonthlyCharges"]) for r in churned),
            }
        )
    return sorted(output, key=lambda x: (-float(x["churn_rate"]), str(x["segment"])))


def retention_curve(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    total = len(rows)
    for month in [1, 3, 6, 12, 24, 36, 48, 60, 72]:
        retained = sum(int(r["tenure"]) >= month and r["ChurnFlag"] == 0 for r in rows)
        observed = sum(int(r["tenure"]) >= month for r in rows)
        churned_at_or_before = sum(int(r["tenure"]) <= month and r["ChurnFlag"] == 1 for r in rows)
        output.append(
            {
                "month": month,
                "observed_customers": observed,
                "active_customers": retained,
                "active_share_of_total": retained / total,
                "churned_at_or_before": churned_at_or_before,
            }
        )
    return output


def analyze(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    churned = [r for r in rows if r["ChurnFlag"] == 1]
    active = [r for r in rows if r["ChurnFlag"] == 0]
    monthly_revenue = sum(float(r["MonthlyCharges"]) for r in rows)
    lost_revenue = sum(float(r["MonthlyCharges"]) for r in churned)

    segments = {
        "contract": summarize_segment(rows, "Contract"),
        "internet_service": summarize_segment(rows, "InternetService"),
        "payment_method": summarize_segment(rows, "PaymentMethod"),
        "tenure": summarize_segment(rows, "TenureBucket"),
        "monthly_charges": summarize_segment(rows, "MonthlyChargeBucket"),
        "protection": summarize_segment(rows, "HasProtection"),
    }

    return {
        "source": "Telco Customer Churn",
        "rows": total,
        "kpis": {
            "customers": total,
            "active_customers": len(active),
            "churned_customers": len(churned),
            "logo_churn_rate": len(churned) / total,
            "monthly_revenue": monthly_revenue,
            "lost_monthly_revenue": lost_revenue,
            "revenue_churn_rate": lost_revenue / monthly_revenue,
            "avg_tenure": sum(float(r["tenure"]) for r in rows) / total,
            "avg_monthly_charges": monthly_revenue / total,
            "month_to_month_churn": next(
                item["churn_rate"] for item in segments["contract"] if item["segment"] == "Month-to-month"
            ),
            "two_year_churn": next(
                item["churn_rate"] for item in segments["contract"] if item["segment"] == "Two year"
            ),
        },
        "segments": segments,
        "retention_curve": retention_curve(rows),
        "churn_profile": {
            "contract": Counter(str(r["Contract"]) for r in churned).most_common(),
            "payment_method": Counter(str(r["PaymentMethod"]) for r in churned).most_common(),
            "internet_service": Counter(str(r["InternetService"]) for r in churned).most_common(),
        },
    }


def bar_chart_svg(
    title: str,
    items: list[dict[str, object]],
    label_key: str,
    value_key: str,
    path: Path,
    value_format: str = "pct",
    accent: str = "#df6c4f",
) -> None:
    width, height = 900, 420
    top, left, row_h = 72, 230, 48
    max_value = max(float(i[value_key]) for i in items) or 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Inter,Arial,sans-serif}.title{font-size:30px;font-weight:800;fill:#18211f}.label{font-size:18px;font-weight:700;fill:#53625d}.value{font-size:18px;font-weight:800;fill:#18211f}.track{fill:#ece6dc}.bar{fill:"
        + accent
        + "}</style>",
        f'<text x="0" y="34" class="title">{html.escape(title)}</text>',
    ]
    for idx, item in enumerate(items):
        y = top + idx * row_h
        label = html.escape(str(item[label_key]))
        value = float(item[value_key])
        bar_w = (width - left - 130) * value / max_value
        display = pct(value) if value_format == "pct" else f"{value:.1f}"
        parts.append(f'<text x="0" y="{y + 25}" class="label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{width-left-130}" height="30" rx="5" class="track"/>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="30" rx="5" class="bar"/>')
        parts.append(f'<text x="{left + bar_w + 12:.1f}" y="{y + 23}" class="value">{display}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def retention_svg(items: list[dict[str, object]], path: Path) -> None:
    width, height = 900, 420
    left, top, chart_w, chart_h = 80, 70, 760, 280
    points = []
    for idx, item in enumerate(items):
        x = left + idx * (chart_w / (len(items) - 1))
        y = top + chart_h - float(item["active_share_of_total"]) * chart_h
        points.append((x, y, item))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in points)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Inter,Arial,sans-serif}.title{font-size:30px;font-weight:800;fill:#18211f}.axis{font-size:15px;font-weight:700;fill:#53625d}.line{fill:none;stroke:#168474;stroke-width:5}.dot{fill:#df6c4f;stroke:white;stroke-width:3}.grid{stroke:#ded7ca;stroke-width:1}</style>",
        '<text x="0" y="34" class="title">Active Customer Retention by Tenure</text>',
    ]
    for pct_line in [0, 0.25, 0.5, 0.75, 1.0]:
        y = top + chart_h - pct_line * chart_h
        parts.append(f'<line x1="{left}" x2="{left + chart_w}" y1="{y}" y2="{y}" class="grid"/>')
        parts.append(f'<text x="8" y="{y + 5}" class="axis">{pct(pct_line)}</text>')
    parts.append(f'<polyline points="{line}" class="line"/>')
    for x, y, item in points:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" class="dot"/>')
        parts.append(f'<text x="{x - 14:.1f}" y="382" class="axis">{item["month"]}</text>')
    parts.append('<text x="390" y="414" class="axis">Tenure month</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_outputs(rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    write_csv(PROCESSED / "telco_churn_cleaned.csv", rows)
    for name, items in summary["segments"].items():
        write_csv(PROCESSED / f"{name}_churn.csv", items)
    write_csv(PROCESSED / "retention_curve.csv", summary["retention_curve"])
    (PROCESSED / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    bar_chart_svg("Churn Rate by Contract", summary["segments"]["contract"], "segment", "churn_rate", CHARTS / "contract_churn.svg")
    bar_chart_svg(
        "Churn Rate by Internet Service",
        summary["segments"]["internet_service"],
        "segment",
        "churn_rate",
        CHARTS / "internet_service_churn.svg",
        accent="#168474",
    )
    bar_chart_svg(
        "Churn Rate by Payment Method",
        summary["segments"]["payment_method"],
        "segment",
        "churn_rate",
        CHARTS / "payment_method_churn.svg",
    )
    bar_chart_svg(
        "Churn Rate by Tenure",
        summary["segments"]["tenure"],
        "segment",
        "churn_rate",
        CHARTS / "tenure_churn.svg",
        accent="#c89b35",
    )
    retention_svg(summary["retention_curve"], CHARTS / "retention_curve.svg")


def table(items: list[dict[str, object]]) -> str:
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item['segment']))}</td>"
            f"<td>{item['customers']}</td>"
            f"<td>{pct(float(item['churn_rate']))}</td>"
            f"<td>{float(item['avg_tenure']):.1f}</td>"
            f"<td>{money(float(item['avg_monthly_charges']))}</td>"
            f"<td>{money(float(item['lost_monthly_revenue']))}</td>"
            "</tr>"
        )
    return (
        "<table><tr><th>Segment</th><th>Customers</th><th>Churn</th><th>Avg tenure</th>"
        "<th>Avg monthly charge</th><th>Lost monthly revenue</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def render_dashboard(summary: dict[str, object]) -> str:
    k = summary["kpis"]
    contract_gap = k["month_to_month_churn"] - k["two_year_churn"]
    cards = [
        ("Customers", f"{k['customers']:,}", "Customer base analyzed"),
        ("Logo churn", pct(k["logo_churn_rate"]), "Customers who left"),
        ("Revenue churn", pct(k["revenue_churn_rate"]), "Monthly revenue at risk"),
        ("Lost monthly revenue", money(k["lost_monthly_revenue"]), "MRR tied to churned accounts"),
        ("Avg tenure", f"{k['avg_tenure']:.1f} mo", "Observed customer lifetime"),
        ("Contract risk gap", f"+{contract_gap * 100:.1f} pts", "Month-to-month vs two-year churn"),
    ]
    card_html = "".join(
        f"<section><span>{label}</span><strong>{value}</strong><p>{detail}</p></section>"
        for label, value, detail in cards
    )

    insights = [
        "Month-to-month contracts are the biggest retention risk and churn far above one-year and two-year customers.",
        "Fiber optic customers churn more than DSL and no-internet-service customers, suggesting price, reliability, or support expectations need attention.",
        "Electronic check users show elevated churn and deserve payment-experience and save-offer testing.",
        "Early-tenure customers are most fragile; churn drops sharply once customers reach longer tenure bands.",
    ]
    recommendations = [
        ("Move risky users off monthly contracts", "Offer annual-contract discounts, pause options, and loyalty credits before renewal."),
        ("Fix fiber optic churn drivers", "Audit support tickets, pricing perception, and service quality for fiber customers."),
        ("Improve payment experience", "Nudge electronic-check customers toward auto-pay/card options with reminder and recovery flows."),
        ("Protect the first year", "Create onboarding, service education, and proactive support campaigns for customers under 12 months tenure."),
    ]
    insight_html = "".join(f"<li>{html.escape(i)}</li>" for i in insights)
    rec_html = "".join(f"<article><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></article>" for t, d in recommendations)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FUTURE_DS_02 | Telecom Churn Dashboard</title>
  <style>
    :root {{
      --ink:#18211f; --muted:#5f6c68; --paper:#f7f4ee; --panel:#fffdf8;
      --line:#ded7ca; --teal:#168474; --coral:#df6c4f; --gold:#c89b35;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--paper); color:var(--ink); font-family:Inter,Arial,sans-serif; line-height:1.45; }}
    header {{ padding:48px clamp(18px,5vw,72px) 110px; color:#fffdf8; background:linear-gradient(120deg,rgba(24,33,31,.96),rgba(24,33,31,.78)), repeating-linear-gradient(135deg,#26332f 0 3px,#31413d 3px 16px); }}
    .eyebrow {{ color:#f4c76c; font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
    h1 {{ margin:10px 0 12px; max-width:980px; font-size:clamp(2.3rem,6vw,5.1rem); line-height:.98; letter-spacing:0; }}
    header p {{ max-width:820px; color:#d9e1dd; font-size:1.08rem; }}
    main {{ padding:0 clamp(18px,4vw,56px) 52px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(6,minmax(140px,1fr)); gap:14px; margin-top:-70px; }}
    .kpis section, .panel {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); box-shadow:0 12px 28px rgba(36,48,45,.08); }}
    .kpis section {{ min-height:140px; padding:18px; }}
    .kpis span {{ color:var(--muted); font-size:.78rem; font-weight:800; text-transform:uppercase; }}
    .kpis strong {{ display:block; margin:10px 0 6px; font-size:clamp(1.45rem,2.6vw,2.15rem); }}
    .kpis p {{ margin:0; color:var(--muted); font-size:.9rem; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; margin-top:24px; }}
    .panel {{ padding:22px; overflow:hidden; }}
    .full {{ grid-column:1/-1; }}
    h2 {{ margin:0 0 16px; font-size:clamp(1.35rem,2.2vw,2rem); }}
    h3 {{ margin:0 0 8px; font-size:1rem; }}
    img {{ width:100%; height:auto; display:block; }}
    table {{ width:100%; border-collapse:collapse; font-size:.92rem; }}
    th,td {{ padding:10px 9px; border-bottom:1px solid var(--line); text-align:left; }}
    th {{ color:var(--muted); font-size:.74rem; text-transform:uppercase; letter-spacing:.06em; }}
    ul {{ margin:0; padding-left:20px; }}
    li {{ margin-bottom:10px; }}
    .recommendations {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }}
    .recommendations article {{ border-left:5px solid var(--gold); padding:8px 12px; background:#fbf6ea; border-radius:0 8px 8px 0; }}
    .recommendations p {{ margin:0; color:var(--muted); }}
    footer {{ padding:0 clamp(18px,4vw,56px) 34px; color:var(--muted); }}
    @media (max-width:1100px) {{ .kpis {{ grid-template-columns:repeat(3,1fr); }} .recommendations {{ grid-template-columns:repeat(2,1fr); }} }}
    @media (max-width:760px) {{ header {{ padding-bottom:92px; }} .kpis,.grid,.recommendations {{ grid-template-columns:1fr; }} .panel {{ overflow-x:auto; }} }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">FUTURE_DS_02 · Telecom customer churn</div>
    <h1>Retention risk is highest in flexible, early-tenure accounts.</h1>
    <p>Dashboard built from a telecom customer churn dataset with contract, tenure, service, payment, and billing behavior.</p>
  </header>
  <main>
    <section class="kpis">{card_html}</section>
    <section class="grid">
      <article class="panel"><h2>Contract Risk</h2><img src="charts/contract_churn.svg" alt="Churn rate by contract"></article>
      <article class="panel"><h2>Internet Service Risk</h2><img src="charts/internet_service_churn.svg" alt="Churn rate by internet service"></article>
      <article class="panel"><h2>Payment Method Risk</h2><img src="charts/payment_method_churn.svg" alt="Churn rate by payment method"></article>
      <article class="panel"><h2>Tenure Pattern</h2><img src="charts/tenure_churn.svg" alt="Churn rate by tenure"></article>
      <article class="panel full"><h2>Customer Lifetime Pattern</h2><img src="charts/retention_curve.svg" alt="Active customer retention curve"></article>
      <article class="panel"><h2>Contract Segment Table</h2>{table(summary["segments"]["contract"])}</article>
      <article class="panel"><h2>Payment Segment Table</h2>{table(summary["segments"]["payment_method"])}</article>
      <article class="panel"><h2>Executive Insights</h2><ul>{insight_html}</ul></article>
      <article class="panel"><h2>Retention Recommendations</h2><div class="recommendations">{rec_html}</div></article>
    </section>
  </main>
  <footer>Source file: <code>data/raw/telco_customer_churn.csv</code>. Rebuild with <code>python3 scripts/build_telecom_churn_report.py</code>.</footer>
</body>
</html>
"""


def main() -> None:
    rows = read_rows()
    summary = analyze(rows)
    write_outputs(rows, summary)
    html_text = render_dashboard(summary)
    DASHBOARD.write_text(html_text, encoding="utf-8")
    INDEX.write_text(html_text.replace('src="charts/', 'src="outputs/charts/'), encoding="utf-8")
    print(f"Built dashboard: {DASHBOARD}")
    print(f"Customers: {summary['kpis']['customers']:,}")
    print(f"Logo churn: {pct(summary['kpis']['logo_churn_rate'])}")


if __name__ == "__main__":
    main()
