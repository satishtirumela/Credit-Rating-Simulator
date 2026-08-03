import subprocess
import time

gcloud_bin = r"C:\Users\DELL\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
auth_code = "4/0AXEQxIBdB6QI3jukV1IL2Z5DkOkf6kU8V5R2FuhdjlGUcYOnN3Mn4R6OdDUcz-79el19Sg"

print("Starting gcloud auth login subprocess...")
proc = subprocess.Popen(
    [gcloud_bin, "auth", "login", "--no-launch-browser"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(2)
out, err = proc.communicate(input=auth_code + "\n", timeout=30)
print("STDOUT:", out)
print("STDERR:", err)
print("RETURN CODE:", proc.returncode)
