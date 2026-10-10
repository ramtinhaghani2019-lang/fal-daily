import re
import requests
from bs4 import BeautifulSoup

# اطلاعات ربات تلگرام
TELEGRAM_BOT_TOKEN = "8752620105:AAE4RnZVq0gspn8ph7G-173GDWi5IceewOQ"
TELEGRAM_CHAT_ID = "40581962"

BASE_URL = "https://uptune.ir/fal/"
SIGNATURE = "\n—————————————————————\nحکمت سلیمانی\n@Hekmate_Soleymani"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MONTHS = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def get_links():
    res = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = {"hafez": None, "abjad": None, "coffee": None}
    
    for a in soup.find_all('a', href=True):
        title = a.get_text(strip=True)
        href = a['href']
        if "فال حافظ امروز" in title and not links["hafez"]:
            links["hafez"] = href
        elif "فال ابجد امروز" in title and not links["abjad"]:
            links["abjad"] = href
        elif "فال قهوه امروز" in title and not links["coffee"]:
            links["coffee"] = href
        if all(links.values()):
            break
    return links

def process_post(post_url, default_title):
    res = requests.get(post_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    h1 = soup.find('h1')
    title = h1.get_text(strip=True) if h1 else default_title
    
    content_area = soup.find('article') or soup.find('div', class_=re.compile(r'content|post-body|entry'))
    text = content_area.get_text("\n") if content_area else soup.get_text("\n")
    
    months_data = {}
    for m in MONTHS:
        pattern = rf"(فال.*?متولدین {m}.*?)(?=(فال.*?متولدین|$))"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            months_data[m] = match.group(1).strip()
        else:
            months_data[m] = f"متن متولدین {m} یافت نشد."

    groups = [
        ["فروردین", "اردیبهشت", "خرداد"],
        ["تیر", "مرداد", "شهریور"],
        ["مهر", "آبان", "آذر"],
        ["دی", "بهمن", "اسفند"]
    ]
    
    for grp in groups:
        box_text = f"🗓 {title}\n\n"
        box_text += "\n—————————————————————\n".join([months_data[m] for m in grp if m in months_data])
        box_text += SIGNATURE
        send_telegram(f"```text\n{box_text}\n```")

def main():
    links = get_links()
    if links["hafez"]:
        process_post(links["hafez"], "فال حافظ")
    if links["abjad"]:
        process_post(links["abjad"], "فال ابجد")
    if links["coffee"]:
        process_post(links["coffee"], "فال قهوه")

if __name__ == "__main__":
    main()
