import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

# Example URL to one of the index.html pages
base_url = "https://www.malware-traffic-analysis.net/2025/07/23/index.html"
session = requests.Session()

# Set headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Get HTML page
response = session.get(base_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all ZIP links
for link in soup.find_all('a', href=True):
    href = link['href']
    if href.endswith('.zip'):
        zip_url = urljoin(base_url, href)
        zip_name = href.split('/')[-1]

        print(f"Downloading: {zip_url}")
        r = session.get(zip_url, headers=headers)
        with open(zip_name, 'wb') as f:
            f.write(r.content)
