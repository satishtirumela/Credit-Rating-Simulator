import os
import difflib

templates = ["home.html", "upload.html", "review.html", "results.html"]

print("================================================================================")
print("COMPARING FRONTEND COPIES: app/templates/ vs public/")
print("================================================================================")

for t in templates:
    app_path = os.path.join("app", "templates", t)
    pub_path = os.path.join("public", t)
    
    print(f"\n--- SCREEN: {t} ---")
    if not os.path.exists(app_path):
        print(f"MISSING in app/templates/: {app_path}")
        continue
    if not os.path.exists(pub_path):
        print(f"MISSING in public/: {pub_path}")
        continue
        
    with open(app_path, "r", encoding="utf-8") as f:
        app_lines = f.readlines()
    with open(pub_path, "r", encoding="utf-8") as f:
        pub_lines = f.readlines()
        
    diff = list(difflib.unified_diff(app_lines, pub_lines, fromfile=app_path, tofile=pub_path, n=1))
    
    if not diff:
        print("--> 100% IDENTICAL")
    else:
        print(f"--> DIFF DETECTED ({len(diff)} diff lines)")
        print("Diff Summary:")
        for line in diff[:15]:
            print("  ", line.strip())

print("\n================================================================================")
