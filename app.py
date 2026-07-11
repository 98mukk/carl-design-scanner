"""CARL — Copy · Analyze · Rulebook · Launch.

Wraps the Firecrawl scrape API, then runs the Sharingan Scan:
extracts colors, fonts, shape tokens, and section order from the
target site and returns a 6-line rulebook draft.
"""

import os
import re
from collections import Counter

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

FIRECRAWL_URL = "https://api.firecrawl.dev/v2/scrape"
API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

app = FastAPI(title="CARL")


class ScanRequest(BaseModel):
    url: str


def firecrawl_scrape(url: str) -> dict:
    if not API_KEY:
        raise HTTPException(500, "FIRECRAWL_API_KEY missing — add it to .env")
    resp = requests.post(
        FIRECRAWL_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"url": url, "formats": ["markdown", "rawHtml"], "onlyMainContent": False},
        timeout=90,
    )
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, f"Firecrawl error: {resp.text[:300]}")
    data = resp.json().get("data", {})
    if not data:
        raise HTTPException(502, "Firecrawl returned no data for that URL")
    return data


HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}\"]+)", re.IGNORECASE)
RADIUS_RE = re.compile(r"border-radius\s*:\s*([^;}\"]+)", re.IGNORECASE)
CSSVAR_RE = re.compile(r"(--[a-zA-Z][\w-]*)\s*:\s*([^;}]+)")
HEADING_RE = re.compile(r"<(h[12])[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def analyze(html: str, markdown: str, meta: dict) -> dict:
    colors = Counter(c.lower() for c in HEX_RE.findall(html))

    fonts: list[str] = []
    for match in FONT_RE.findall(html):
        family = match.split(",")[0].strip().strip("'\"")
        if family and not family.startswith(("var(", "-")) and family not in fonts:
            fonts.append(family)

    radii = sorted(
        {r.strip() for r in RADIUS_RE.findall(html) if not r.strip().startswith("var(")}
    )

    css_vars = {}
    for name, value in CSSVAR_RE.findall(html):
        if len(css_vars) < 40 and name not in css_vars:
            css_vars[name] = value.strip()

    sections = []
    for _, raw in HEADING_RE.findall(html):
        text = TAG_RE.sub("", raw).strip()
        if text and len(text) < 90 and text not in sections:
            sections.append(text)

    return {
        "title": meta.get("title", ""),
        "description": meta.get("description", ""),
        "colors": [{"hex": h, "count": n} for h, n in colors.most_common(12)],
        "fonts": fonts[:6],
        "radii": radii[:8],
        "css_vars": css_vars,
        "sections": sections[:12],
        "markdown_preview": markdown[:1500],
    }


@app.post("/scan")
def scan(req: ScanRequest):
    url = req.url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    data = firecrawl_scrape(url)
    report = analyze(data.get("rawHtml", ""), data.get("markdown", ""), data.get("metadata", {}))
    report["url"] = url
    return report


@app.get("/")
def home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
