# CARL 🕷️ — Copy · Analyze · Rulebook · Launch
Firecrawl wrapper that runs the Sharingan Scan on any website and drafts your 6-line design rulebook. UI uses the official Solana brand palette (purple #9945FF, green #14F195) on near-black — colors only, no Solana marks (their brand guidelines prohibit logo reuse).

## Run it
```bash
cd ~/Desktop/Hypothesis/CARL
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your Firecrawl key (firecrawl.dev → API Keys)
uvicorn app:app --reload
```
Open http://127.0.0.1:8000 — paste a URL, hit **Run Scan**.

## What's what
- `app.py` — FastAPI backend: wraps Firecrawl `/v2/scrape`, extracts colors / fonts / radii / sections from the HTML.
- `static/index.html` — the black & gold UI (Steel & Signal tokens + Solana dark-technical discipline).
- `FRAMEWORK.md` — the repeatable CARL framework, course outline, and marketing/sales playbook. **This is the teachable asset.**

## Design lineage
Rebuilt with the design-taste-frontend skill (anti-slop rules) + Solana brand palette + ethereum.org UX principles (labeled inputs, visible loading/error/empty states, plain language). Color rule: purple = identity and interactive accent, green = action (CTA) and success only.
