from flask import Flask, Response, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Pingr/1.0 (hello@pingr.com)",
    "From": "hello@pingr.com",
    "Accept": "text/plain",
}

def quarter_for_date(d: datetime) -> str:
    q = (d.month - 1) // 3 + 1
    return f"QTR{q}"

def master_idx_url(d: datetime) -> str:
    y = d.year
    qtr = quarter_for_date(d)
    datestr = d.strftime("%Y%m%d")
    return f"https://sec.gov/Archives/edgar/daily-index/{y}/{qtr}/master.{datestr}.idx"

def fetch_text(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {url}")
    return r.text

def filter_form4_lines(text: str):
    lines = []
    for line in text.splitlines():
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) != 5:
            continue
        form_type = parts[2].strip()
        if form_type in ("4", "4/A"):
            lines.append(line)
    return lines

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/form4-index")
def form4_index():
    days_back = int(request.args.get("days_back", "7"))
    max_days = min(max(days_back, 1), 30)

    for i in range(0, max_days + 1):
        d = datetime.utcnow() - timedelta(days=i)
        url = master_idx_url(d)
        try:
            text = fetch_text(url)
            lines = filter_form4_lines(text)
            body = "\n".join(lines) + "\n"
            return Response(body, mimetype="text/plain")
        except Exception:
            continue

    return Response("ERROR: could not fetch recent master.idx\n", status=500, mimetype="text/plain")
