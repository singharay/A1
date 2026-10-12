# India Geopolitical-to-Sector Daily Monitor

A scheduled Claude-powered research agent that scans current geopolitical news and
assesses likely impact on Indian listed-equity sectors. It runs daily at **8:00 AM
India Standard Time** through GitHub Actions, with a manual "Run workflow" option.

## What the report contains

- Executive summary of the most material verified geopolitical developments
- Highest positive and negative sector impacts
- A scored table covering all 26 sectors in `main.py`
- Impact direction: positive, negative, mixed, or neutral
- Score from 1 to 10, confidence, horizon, rationale and source links
- Cross-sector transmission channels and a "what to watch next" list

### Score meaning

| Score | Meaning |
|---:|---|
| 1–2 | Exceptionally/severely adverse sector impact |
| 3–4 | Adverse |
| 5 | Neutral, mixed, or no material verified update |
| 6–7 | Beneficial |
| 8–9 | Materially beneficial |
| 10 | Strongly beneficial |

This is a **sector-impact score**, not an expected share-price return, a probability,
or a buy/sell recommendation. The same event can benefit one sector and hurt another.

## Deployment: GitHub Actions (cloud)

1. Create a private GitHub repository and upload these files.
2. In Anthropic Console, create an API key. API use and web search may incur charges.
3. In the repository, open **Settings → Secrets and variables → Actions**.
4. Under **Secrets**, add `ANTHROPIC_API_KEY`.
5. Optional: under **Variables**, add `CLAUDE_MODEL` (default `claude-sonnet-5`)
   and `MAX_SEARCHES` (default `12`).
6. Open **Actions → Daily India Geopolitical Sector Monitor → Run workflow** to test.
7. For the daily report, open the completed workflow run and download its artifact.

GitHub Actions scheduled workflows can be delayed during high load and depend on
the repository's Actions availability. The workflow uses UTC cron: `02:30 UTC` =
`08:00 IST`.

## Optional email delivery

The agent can email the Markdown report after generation. Configure these under
**Settings → Secrets and variables → Actions**:

**Secrets:** `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO`.
Optionally set `SMTP_FROM` and `EMAIL_FROM` as secrets.
**Variables:** `SMTP_PORT` (usually `587`).

Use an app password or provider-approved SMTP credentials, not your normal account
password. If SMTP is not configured, the report is still saved as a workflow artifact.

## Run locally (Windows 11 / macOS / Linux)

Python 3.11+ is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY="your_api_key"
python main.py
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_api_key"
python main.py
```

The Markdown report is saved under `reports/`.

## Cost and coverage controls

- `MAX_SEARCHES` limits the number of server-side web searches per run. More searches
  may improve coverage but increase cost. The model can search several stories in
  one query, but a search cap means coverage is not guaranteed exhaustive.
- Anthropic web search is billed separately from model tokens; check the current
  Anthropic pricing page before enabling daily runs.
- Change `CLAUDE_MODEL` to a model enabled for your API account. Model IDs and pricing
  change over time.
- Treat low-confidence items as prompts for further research, not as facts.
- Do not use the score alone to place trades. Review the linked source, earnings
  exposure, valuation and market expectations.

## Important implementation note

This uses the **Anthropic API**, not just a Claude Pro chat subscription. A Claude
chat subscription and API billing are separate. The report is research support,
not financial advice.
