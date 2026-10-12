import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import anthropic

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime.now(IST)
DATE = NOW.strftime("%Y-%m-%d")
OUT_DIR = Path("reports")
OUT_DIR.mkdir(exist_ok=True)

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
MAX_SEARCHES = int(os.getenv("MAX_SEARCHES", "12"))

SECTORS = [
    "Oil & Gas (upstream, gas, LNG)",
    "Oil Marketing Companies (OMCs)",
    "Paints",
    "Tyres and rubber products",
    "Aviation and airlines",
    "Shipping, ports and marine logistics",
    "Logistics, freight and warehousing",
    "Fertilisers",
    "Agrochemicals",
    "IT services and consulting",
    "Pharmaceuticals and APIs",
    "Semiconductors and electronics manufacturing",
    "Defence and aerospace",
    "Metals, mining and critical minerals",
    "Renewable energy, solar, wind and batteries",
    "Automobiles and auto components",
    "Banks, NBFCs and capital markets",
    "Insurance",
    "FMCG and consumer durables",
    "Telecom and data centres",
    "Tourism, hotels and travel services",
    "Gold, jewellery and precious metals",
    "Textiles and apparel",
    "Cement, construction and infrastructure",
    "Power utilities and electricity generation",
    "Food processing and agricultural products",
]

SYSTEM_PROMPT = """
You are a rigorous geopolitical-risk analyst for Indian listed equities.
Prepare a source-backed DAILY geopolitical-to-sector impact report. You are not
a stock promoter and must not provide guaranteed predictions or personalized
investment advice.

Research rules:
- Search for the latest material geopolitical developments relevant to India
  and the Indian equity sectors in the user prompt. Prioritise developments
  from the last 24 hours; use up to 7 days only if still material and clearly
  label the event date. State the report timestamp in Asia/Kolkata time.
- Prefer primary sources (government, regulator, central bank, company filings,
  official statements) and reputable newswires/outlets. Cross-check major claims
  when possible. Do not treat search snippets as established fact if the page
  does not support them.
- Distinguish confirmed facts, reported claims, and analytical inference.
  Do not invent events, dates, company exposures, prices, or citations.
- Deduplicate stories describing the same event. Explain the transmission
  mechanism from trigger to sector economics: commodity/input costs, demand,
  exports, FX, freight, sanctions/compliance, supply chain, interest rates,
  capital flows, government policy or valuation/risk premium.
- Cover EVERY sector listed in the user prompt. If no material new trigger is
  found for a sector, say "No material verified update found" and use a score
  of 5 with low confidence; do not invent a trigger.
- A single trigger can affect sectors in opposite directions. Score each sector
  separately, based on its likely fundamental exposure, not headline sentiment.
- Include source URLs inline for every material event. Use markdown links.
  If reliable source links cannot be established, mark the claim unverified and
  do not score it as a high-confidence event.

Scoring rubric (sector-specific impact, not expected stock return):
10 = strongly beneficial; 8-9 = materially beneficial; 6-7 = mildly beneficial;
5 = neutral, mixed, or no material verified update; 3-4 = mildly/materially
adverse; 2 = severely adverse; 1 = exceptionally adverse / major disruption.
For each score include direction (POSITIVE / NEGATIVE / MIXED / NEUTRAL),
impact horizon (intraday / days-weeks / months), confidence (LOW / MEDIUM /
HIGH), and a short rationale. Score the impact of the geopolitical trigger on
the sector's operating environment/earnings outlook, not whether the stock is
certain to rise or fall. Explain uncertainty and any important offsetting effects.

Output format:
1. Executive summary: 3-7 most important developments and overall risk tone.
2. "Highest positive sector impacts" and "Highest negative sector impacts".
3. A complete sector table with columns:
   Sector | Relevant trigger/update (with date and source links) | Direction |
   Score (1-10) | Confidence | Horizon | Why it matters / key caveat.
4. "Cross-sector transmission" summarising commodity, FX, rates, trade,
   shipping, sanctions, capital-flow and supply-chain channels where relevant.
5. "What to watch next" with specific upcoming events/indicators and dates only
   where verified.
6. Sources list with publisher, headline, publication date if available, URL.
7. A compact JSON block at the end with keys:
   report_date_ist, executive_tone, key_events (array), sector_scores (array
   of objects with sector, direction, score, confidence, horizon, trigger,
   rationale, sources array), watchlist (array).
Keep the report decision-useful, concise but complete. Do not claim exhaustive
news coverage. If a sector has no verified update, still include it.
"""

def send_email(subject: str, body: str) -> None:
    """Optional email delivery; only runs when SMTP settings are configured."""
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    to_addr = os.getenv("EMAIL_TO")
    from_addr = os.getenv("EMAIL_FROM") or os.getenv("SMTP_FROM") or user
    if not all([host, user, password, to_addr, from_addr]):
        print("Email not configured; report will be available as a workflow artifact.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    print(f"Email report sent to {to_addr}")

def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        return 2

    client = anthropic.Anthropic()
    sector_lines = "\n".join(f"- {s}" for s in SECTORS)
    user_prompt = f"""
Create the daily report for {NOW.strftime('%A, %d %B %Y, %I:%M %p IST')}.

Coverage universe — cover every sector below:
{sector_lines}

Geopolitical themes to actively scan include, but are not limited to:
Middle East conflicts and Strait of Hormuz; Red Sea/Suez and maritime security;
Russia-Ukraine and sanctions; US-China strategic rivalry, tariffs, Taiwan Strait
and South China Sea; India-US trade and tariff negotiations; India-China and
India-Pakistan tensions; OPEC+ and oil/gas supply; critical minerals and rare
earth export controls; defence alliances and procurement; cyberwarfare;
semiconductor/AI export controls; immigration and visa rules; carbon-border
measures; food/fertiliser export restrictions; global elections and policy
reversals; sovereign yields, dollar strength and cross-border capital flows;
and ceasefires, diplomatic agreements or de-escalation.

Assess only plausible, explainable sector transmission. A geopolitical event
need not be negative: trade diversion, domestic substitution, higher commodity
realisation or defence orders can benefit some sectors while hurting others.
Use current verified evidence and cite links. Include a score for every sector.
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=12000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCHES,
        }],
    )

    text_parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)
    report = "\n\n".join(text_parts).strip()
    if not report:
        print("ERROR: Claude returned no text report.", file=sys.stderr)
        return 3

    output_path = OUT_DIR / f"india-geopolitical-sector-report-{DATE}.md"
    output_path.write_text(
        f"# India Geopolitical-to-Sector Daily Monitor\n\n"
        f"**Generated:** {NOW.strftime('%Y-%m-%d %H:%M IST')}  \n"
        f"**Model:** `{MODEL}`  \n"
        f"**Search limit:** {MAX_SEARCHES} web searches per run\n\n"
        f"> Scores are analytical assessments of sector impact, not forecasts of "
        f"stock returns. Verify sources and use independent judgment.\n\n"
        f"{report}\n",
        encoding="utf-8",
    )
    print(f"Report saved to {output_path}")
    send_email(f"India Geopolitical Sector Monitor — {DATE}", report)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
