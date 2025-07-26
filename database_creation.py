import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from zipfile import ZipFile
from time import sleep

# -------------------------------
# CONFIG
BASE_URL = "https://www.malware-traffic-analysis.net/"
WORK_DIR = "malware_zips"
DEST_DIR = "pcap_database"
NUM_TO_DOWNLOAD = 10  # Change to more later
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# -------------------------------
# SETUP
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

# -------------------------------
# HELPER FUNCTIONS

def get_analysis_pages():
    """Get all blog post links (ending in .html)"""
    r = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.select("li a"):
        href = a.get("href", "")
        if href.startswith("20") and href.endswith(".html"):
            links.append(urljoin(BASE_URL, href))
    return links

def find_zip_and_download(page_url, count):
    """Download and extract PCAP ZIPs with date-based password"""
    r = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        if a["href"].endswith(".zip"):
            zip_url = urljoin(page_url, a["href"])
            zip_name = zip_url.split("/")[-1]
            zip_path = os.path.join(WORK_DIR, zip_name)

            if os.path.exists(zip_path):
                print(f"[{count}] Already downloaded: {zip_name}")
                return False

            print(f"[{count}] Downloading: {zip_name}")
            with requests.get(zip_url, headers=HEADERS, stream=True) as resp:
                with open(zip_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)

            extract_zip(zip_path)
            return True
    return False

def extract_zip(zip_path):
    """Extract .pcap/.pcapng from ZIP using infected_YYYYMMDD password"""
    name = os.path.basename(zip_path)
    if not name[:10].count("-") == 2:
        print(f"❌ Skipping malformed filename: {name}")
        return

    date_str = name[:10].replace("-", "")  # e.g., 20250725
    password = f"infected_{date_str}"

    try:
        with ZipFile(zip_path) as zf:
            for file in zf.namelist():
                if file.endswith((".pcap", ".pcapng")):
                    zf.extract(file, path=DEST_DIR, pwd=password.encode())
                    print(f"✅ Extracted: {file}")
    except Exception as e:
        print(f"❌ Failed to extract {name} with password {password}: {e}")

# -------------------------------
# MAIN LOGIC

print("🔍 Fetching analysis pages...")
pages = get_analysis_pages()
downloaded = 0

for i, link in enumerate(pages):
    if downloaded >= NUM_TO_DOWNLOAD:
        break
    if find_zip_and_download(link, downloaded + 1):
        downloaded += 1
        sleep(2)

print(f"\n✅ All done. {downloaded} PCAPs downloaded to {DEST_DIR}")
