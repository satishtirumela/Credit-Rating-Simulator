import os
import hashlib

corpus_dir = r"c:\Users\DELL\projects\Credit-Rating-Simulator\corpus"

print("================================================================================")
print("INSPECTING LOCAL CORPUS FILES IN:", corpus_dir)
print("================================================================================")

files = sorted(os.listdir(corpus_dir))
for f in files:
    fp = os.path.join(corpus_dir, f)
    if os.path.isfile(fp):
        size = os.path.getsize(fp)
        with open(fp, "rb") as buf:
            data = buf.read()
        sha = hashlib.sha256(data).hexdigest()
        print(f"{f:70s} | Size: {size:8d} bytes | SHA: {sha[:16]}...")

print("================================================================================")
