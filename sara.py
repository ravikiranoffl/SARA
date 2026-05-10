import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
from datetime import datetime, timezone, timedelta

# Configuration
FEEDS = {
    "The_Hindu_Telangana": "https://www.thehindu.com/news/national/telangana/feeder/default.rss",
    "The_Hindu_Andhra_Pradesh": "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss",
    "AIR_News_Regional": "https://newsonair.gov.in/category/regional-news/feed/"
}

def get_ist_time():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return ET.fromstring(response.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    ist_now = get_ist_time()
    year = ist_now.strftime("%Y")
    month_folder = ist_now.strftime("%m-%B")
    filename = ist_now.strftime("%d-%m-%Y.json")
    
    # Path: Archive/2026/05-May/10-05-2026.json
    dir_path = os.path.join("Archive", year, month_folder)
    os.makedirs(dir_path, exist_ok=True)
    full_path = os.path.join(dir_path, filename)

    # Load existing data for the day
    daily_data = {}
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)

    for source, url in FEEDS.items():
        root = fetch_rss(url)
        if root is None: continue
        
        if source not in daily_data:
            daily_data[source] = []

        # Track existing IDs to prevent duplicates
        existing_ids = {item['id'] for item in daily_data[source]}

        for item in root.findall('.//item'):
            title = item.find('title').text.strip() if item.find('title') is not None else ""
            link = item.find('link').text.strip() if item.find('link') is not None else ""
            desc = item.find('description').text.strip() if item.find('description') is not None else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""

            # Create a unique ID based on the link
            entry_id = hashlib.md5(link.encode()).hexdigest()

            if entry_id not in existing_ids:
                daily_data[source].append({
                    "id": entry_id,
                    "time_extracted": ist_now.strftime("%H:%M:%S"),
                    "title": title,
                    "description": desc,
                    "url": link,
                    "published": pub_date
                })

    # Save with clean formatting
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
