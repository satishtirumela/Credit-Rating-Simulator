import hashlib
import csv
import os

corpus_dir = r"c:\Users\DELL\projects\Credit-Rating-Simulator\corpus"
fname = "CARE_Criteria_for_Infrastructure_Sector_Ratings_Mar_2025.pdf"
fpath = os.path.join(corpus_dir, fname)

print("================================================================================")
print("COMPUTING SHA-256 FOR LOCAL CORPUS FILE:", fname)
print("================================================================================")

if os.path.exists(fpath):
    with open(fpath, "rb") as f:
        file_bytes = f.read()
    local_sha = hashlib.sha256(file_bytes).hexdigest()
    print("Local File Size:", len(file_bytes), "bytes")
    print("Computed Local SHA-256:", local_sha)
else:
    print("Local file DOES NOT EXIST:", fpath)

manifest_path = os.path.join(corpus_dir, "Reference_Corpus_Manifest_v3_0.csv")
print("\nManifest Path:", manifest_path)
if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as mf:
        reader = csv.DictReader(mf)
        found = False
        for row in reader:
            if row.get("filename", "").strip() == fname:
                found = True
                print("Manifest Recorded filename:", row.get("filename"))
                print("Manifest Recorded sha256:  ", row.get("sha256"))
                if local_sha == row.get("sha256", "").strip():
                    print("--> MATCH: Local file SHA-256 matches manifest exactly!")
                else:
                    print("--> MISMATCH: Local file SHA-256 DOES NOT match manifest!")
        if not found:
            print("Filename NOT FOUND in manifest CSV!")
else:
    print("Manifest CSV DOES NOT EXIST!")

print("================================================================================")
