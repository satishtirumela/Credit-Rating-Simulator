import urllib.request
import re

opener = urllib.request.build_opener(urllib.request.ProxyHandler())

urls = [
    "https://credit-rating-simulator.web.app/results/TP-2-Mid-Wind",
    "https://credit-rating-simulator.web.app/upload",
    "https://credit-rating-simulator.web.app/backtest",
    "https://credit-rating-simulator.web.app/review/TP-2-Mid-Wind",
    "https://credit-rating-simulator.web.app/"
]

print("================================================================================")
print("LIVE VERIFICATION OF ALL 5 FIREBASE HOSTING / CLOUD RUN URLS")
print("================================================================================")

for url in urls:
    try:
        req = opener.open(url, timeout=15)
        status = req.getcode()
        body = req.read().decode("utf-8")
        snippet = body[:400].replace("\r\n", "\n")
        print(f"\nURL: {url}")
        print(f"HTTP Status: {status}")
        print(f"Literal Snippet:\n{snippet}\n")
        
        if url == "https://credit-rating-simulator.web.app/":
            # Search for 'New Assessment' button href/onclick
            matches = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>.*?New Assessment.*?</a>', body, re.IGNORECASE | re.DOTALL)
            if not matches:
                matches = re.findall(r'<button[^>]*onclick="([^"]*)"[^>]*>.*?New Assessment.*?</button>', body, re.IGNORECASE | re.DOTALL)
            print(f"-> 'New Assessment' Button Action/Link Found: {matches if matches else 'Check full markup'}")
    except Exception as e:
        print(f"\nURL: {url}")
        print(f"Error: {e}")

print("================================================================================")
