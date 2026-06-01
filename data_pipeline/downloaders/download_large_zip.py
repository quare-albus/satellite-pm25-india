import os
import time
import zipfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================
# CONFIG
# =========================

URL = "https://object-store.os-api.cci2.ecmwf.int/cci2-prod-cache-2/2026-05-18/635915c3d5d41463d8d39da31d4d10a.zip"
DOWNLOAD_PATH = "data/raw/era5/era5_data.zip"
EXTRACT_FOLDER = "data/raw/era5/"

# =========================
# CREATE OUTPUT FOLDER
# =========================
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

# =========================
# RETRY SESSION
# =========================
session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retries)

session.mount("http://", adapter)
session.mount("https://", adapter)

# =========================
# RESUME SUPPORT
# =========================
headers = {}

if os.path.exists(DOWNLOAD_PATH):
    downloaded_size = os.path.getsize(DOWNLOAD_PATH)
    headers["Range"] = f"bytes={downloaded_size}-"
    mode = "ab"
    print(f"Resuming from {downloaded_size / (1024*1024):.2f} MB")
else:
    mode = "wb"

# =========================
# DOWNLOAD
# =========================
print("Starting download...")

response = session.get(
    URL,
    headers=headers,
    stream=True,
    timeout=60
)

response.raise_for_status()

with open(DOWNLOAD_PATH, mode) as file:
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            file.write(chunk)

print("Download completed.")

# =========================
# VERIFY ZIP
# =========================
print("Checking ZIP integrity...")

try:
    with zipfile.ZipFile(DOWNLOAD_PATH, 'r') as zip_ref:
        bad_file = zip_ref.testzip()

        if bad_file:
            raise Exception(f"Corrupted file inside ZIP: {bad_file}")

        print("ZIP verified.")

        # =========================
        # EXTRACT
        # =========================
        print("Extracting files...")

        zip_ref.extractall(EXTRACT_FOLDER)

        print(f"Extraction completed to: {EXTRACT_FOLDER}")

except zipfile.BadZipFile:
    print("ZIP file is corrupted.")
except Exception as e:
    print(f"Error: {e}")

# =========================
# OPTIONAL CLEANUP
# =========================
# os.remove(DOWNLOAD_PATH)
# print("Temporary ZIP deleted.")