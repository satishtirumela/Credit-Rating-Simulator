import urllib.request
from pypdf import PdfReader
import io

url = "https://credit-rating-simulator.web.app/api/projects/TP-2-Mid-Wind/download-rationale"
opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(url)

print("================================================================================")
print("DOWNLOADING LIVE RATIONALE PDF FROM:", url)
print("================================================================================")

resp = opener.open(req)
pdf_bytes = resp.read()

print("Downloaded PDF size:", len(pdf_bytes), "bytes")

reader = PdfReader(io.BytesIO(pdf_bytes))
full_text = "\n".join(page.extract_text() for page in reader.pages)

print("\n--- LIVE EXTRACTED PDF TEXT LINES CONTAINING OEM / O&M ---")
for line in full_text.splitlines():
    if "O&M" in line or "OEM" in line:
        print("Line:", repr(line))

if "O&M" in full_text:
    print("\n--> CONFIRMED: 'O&M' is cleanly present in live PDF report!")
else:
    print("\n--> ERROR: 'O&M' missing!")

if "O&M;" in full_text:
    print("--> ERROR: 'O&M;' corrupted entity string found in live PDF!")
else:
    print("--> CONFIRMED: No 'O&M;' corruption found in live PDF report!")

print("================================================================================")
