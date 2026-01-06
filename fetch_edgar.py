import requests
import sys

URL = "https://sec.gov/Archives/edgar/daily-index/2025/QTR1/master.20250102.idx"

headers = {
    "User-Agent": "Pingr/1.0 (hello@pingr.io)",
    "From": "hello@pingr.io",
    "Accept": "text/plain"
}

response = requests.get(URL, headers=headers, timeout=30)

if response.status_code != 200:
    print(f"ERROR {response.status_code}")
    sys.exit(1)

print(response.text)
