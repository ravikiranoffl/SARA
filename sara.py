import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timezone, timedelta

# ==========================================
# SARA: SOUTH INDIA & MAHARASHTRA ARCHIVE
# ==========================================
FEEDS = {
    "News_On_Air_Regional": "https://www.newsonair.gov.in/category/regional-news/feed/",
    "The_Hindu_Telangana": "https://www.thehindu.com/news/national/telangana/feeder/default.rss",
    "The_Hindu_Andhra_Pradesh": "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss",
    "The_Hindu_Karnataka": "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
    "The_Hindu_Tamil_Nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "The_Hindu_Kerala": "https://www.thehindu.com/news/national/kerala/feeder/default.rss",
    "The_Hindu_Maharashtra": "https://www.thehindu.com/news/national/maharashtra/feeder/default.rss"
}

def get_ist_time():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=20) as response:
            return ET.fromstring(response.read())
    except Exception as e:
        print(f"Skipping {url} due to error: {e}")
        return None

def main():
    ist_now = get_ist_time()
    
    # Path logic: YYYY/yyyy-mm-dd.json (e.g., 2026/2026-05-11.json)
    folder_name = ist_now.strftime("%Y")
    file_name = ist_now.strftime("%Y-%m-%d.json")
    
    os.makedirs(folder_name, exist_ok=True)
    full_path = os.path.join(folder_name, file_name)

    # Load existing daily data
    daily_data = {}
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            try:
                daily_data = json.load(f)
            except json.JSONDecodeError:
                daily_data = {}

    for source, url in FEEDS.items():
        root = fetch_rss(url)
        if root is None: continue
        
        if source not in daily_data:
            daily_data[source] = []

        # Headline Filter: Case-insensitive check to ignore existing news
        existing_titles = {str(item.get('Title', '')).lower().strip() for item in daily_data[source]}

        items = root.findall('.//item')
        for item in items:
            t_el = item.find('title')
            l_el = item.find('link')
            d_el = item.find('description')
            p_el = item.find('pubDate')

            title = t_el.text.strip() if (t_el is not None and t_el.text) else ""
            link = l_el.text.strip() if (l_el is not None and l_el.text) else ""
            desc = d_el.text.strip() if (d_el is not None and d_el.text) else ""
            pub_date = p_el.text.strip() if (p_el is not None and p_el.text) else ""

            if not title or not link: continue
            if title.lower() in existing_titles: continue

            # Convention: Title, Description, Article Url, PubDate
            daily_data[source].append({
                "Title": title,
                "Description": desc,
                "Article Url": link,
                "PubDate": pub_date
            })
            existing_titles.add(title.lower())

    # Save finalized JSON
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
