import os

os.makedirs("public", exist_ok=True)
templates = ["home.html", "upload.html", "review.html", "results.html"]

pwa_tags = """    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#3B82F6">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js');
            });
        }
    </script>
"""

for t in templates:
    src = os.path.join("app", "templates", t)
    dst = os.path.join("public", t)
    if os.path.exists(src):
        with open(src, "r", encoding="utf-8") as f:
            content = f.read()

        if "</head>" in content and "/manifest.json" not in content:
            content = content.replace("</head>", pwa_tags + "\n</head>")

        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)

print("Public PWA static templates prepared in public/")
