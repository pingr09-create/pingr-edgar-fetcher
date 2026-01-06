import requests
import sys
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Pingr/1.0 (hello@pingr.io)",
    "From": "hello@pingr.io",
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
    # master.idx has a header; data lines look like:
    # CIK|Company Name|Form Type|Date Filed|Filename
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

def main():
    # Try today, then step back up to 7 days (handles weekends/holidays)
    for i in range(0, 8):
        d = datetime.utcnow() - timedelta(days=i)
        url = master_idx_url(d)
        try:
            text = fetch_text(url)
            lines = filter_form4_lines(text)

            # Print a small header so logs are readable
            print(f"OK {d.strftime('%Y-%m-%d')} {url}")
            print(f"FOUND_FORM4_ROWS={len(lines)}")

            # Print the filtered rows (this is what we’ll feed into n8n next)
            for line in lines:
                print(line)

            return

        except Exception as e:
            print(f"MISS {d.strftime('%Y-%m-%d')} {url} -> {e}")

    print("ERROR: Could not fetch a master.idx file for the last 7 days")
    sys.exit(1)

if __name__ == "__main__":
    main()
