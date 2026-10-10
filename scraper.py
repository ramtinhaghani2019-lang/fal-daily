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

# اطلاعات ماه‌ها و ایموجی‌های فلکی
MONTHS_CONFIG = [
    {"name": "فروردین", "emoji": "♈️ 🌸"},
    {"name": "اردیبهشت", "emoji": "♉️ 🌱"},
    {"name": "خرداد", "emoji": "♊️ 🌿"},
    {"name": "تیر", "emoji": "♋️ 🦀"},
    {"name": "مرداد", "emoji": "♌️ 🦁"},
    {"name": "شهریور", "emoji": "♍️ 🌾"},
    {"name": "مهر", "emoji": "♎️ ⚖️"},
    {"name": "آبان", "emoji": "♏️ 🦂"},
    {"name": "آذر", "emoji": "♐️ 🏹"},
    {"name": "دی", "emoji": "♑️ 🐐"},
    {"name": "بهمن", "emoji": "♒️ 🏺"},
    {"name": "اسفند", "emoji": "♓️ 🐟"}
]

# بانک جامع نمادهای فال قهوه و تعابیر
COFFEE_EMOJIS = {
    "قیچی": "✂️", "راه": "🛣", "پروانه": "🦋", "آهو": "🦌", "آدم": "👤",
    "انسان": "👤", "قلب": "❤️", "زنبور": "🐝", "زنبور عسل": "🐝", "پول": "💰",
    "حلقه گل": "💐", "گل": "🌸", "آب": "💧", "فنجان": "☕️", "در": "🚪",
    "تبر": "🪓", "عینک": "👓", "جعبه": "📦", "گردن بند": "📿", "گردنبند": "📿",
    "آبشار": "🌊", "ساعت": "⏰", "پل": "🌉", "قفل": "🔒", "کلید": "🔑",
    "قفل و کلید": "🔐", "دیگ": "🍲", "لوبیا": "🌱", "شانه": "🪮", "پا": "🦶",
    "تاج": "👑", "کاسه": "🥣", "درخت": "🌳", "عبادتگاه": "🕌", "مسجد": "🕌",
    "فیل": "🐘", "کفتار": "🐺", "حلقه": "💍", "زنگوله": "🔔", "حب": "💊",
    "بادام": "🥜", "خروس": "🐓", "هیزم": "🪵", "میخ": "🔩", "بیل": "⛏",
    "تیر و کمان": "🏹", "کمان": "🏹", "نیزه": "🗡", "استخوان": "🦴", "جارو": "🧹",
    "ترازو": "⚖️", "ماهی": "🐟", "اسب": "🐎", "اسب سوار": "🏇", "تخم مرغ": "🥚",
    "فرم تخم مرغی": "🥚", "سنجاب": "🐿", "صدف": "🐚", "جناغ": "🦴", "چکش": "🔨",
    "اتاق": "🚪", "دیوار": "🧱", "اره": "🪚", "داس": "🌾", "تسبیح": "📿",
    "دانه تسبیح": "📿", "چادر": "⛺️", "خیمه": "⛺️", "کت": "🧥", "خرس": "🐻",
    "پرنده": "🕊", "شیر": "🦁", "مار": "🐍", "ستاره": "⭐️", "کتاب": "📖",
    "قایق": "⛵️", "کشتی": "🚢", "شمع": "🕯", "کفش": "👞", "شمشیر": "⚔️"
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def get_links():
    res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
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

def stylize_body(raw_text, fal_category):
    """پاکسازی تبلیغات و افزودن دقیق ایموجی‌ها به متن فال"""
    lines = raw_text.split('\n')
    cleaned_lines = []
    
    skip_phrases = [
        "دانلود آهنگ", "تلگرام آپ تیون", "اینستاگرام آپ تیون", 
        "در این پست", "مطالب پیشنهادی", "دیدگاه‌ها", "نظرات", 
        "برچسب‌ها", "اشتراک گذاری", "لینک کوتاه"
    ]
    
    for line in lines:
        l = line.strip()
        if not l or l in ["متن", "متن فال:", "متن فال"] or any(sp in l for sp in skip_phrases):
            continue
            
        # ایموجی‌گذاری برای فال حافظ
        if "غزل" in l and ":" in l:
            l = f"📜 {l}"
        elif "تعبیر" in l and ":" in l:
            l = f"🔮 {l}"
            
        # ایموجی‌گذاری برای حروف ابجد
        elif "حروف ابجد" in l:
            l = f"🔤 {l}"
            
        # ایموجی‌گذاری برای نمادهای فال قهوه
        elif fal_category == "coffee":
            matched = False
            for sym, emo in COFFEE_EMOJIS.items():
                if l.startswith(sym + " :") or l.startswith(sym + ":"):
                    l = f"{emo} {l}"
                    matched = True
                    break
            if not matched and ":" in l and not l.startswith("در فال"):
                l = f"☕️ {l}"
                
        cleaned_lines.append(l)
        
    return "\n".join(cleaned_lines)

def process_post(post_url, fal_category, default_title):
    res = requests.get(post_url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    h1 = soup.find('h1')
    raw_title = h1.get_text(strip=True) if h1 else default_title
    clean_title = re.sub(r'\s+', ' ', raw_title).strip()
    
    for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'form', 'noscript']):
        tag.decompose()
        
    content_area = soup.find('article') or soup.find('div', class_=re.compile(r'content|post-body|entry'))
    text = content_area.get_text("\n") if content_area else soup.get_text("\n")
    
    months_data = {}
    for i, m_info in enumerate(MONTHS_CONFIG):
        m_name = m_info["name"]
        m_emoji = m_info["emoji"]
        
        start_pattern = rf"(?:فال.*?متولدین\s*{m_name}.*?)(?:\n|$)"
        if i == len(MONTHS_CONFIG) - 1:
            end_pattern = r"(?:مطالب پیشنهادی|برچسب‌ها|دیدگاه|نظرات|$)"
        else:
            next_name = MONTHS_CONFIG[i+1]["name"]
            end_pattern = rf"(?=(?:فال.*?متولدین\s*{next_name}))"
            
        full_regex = rf"{start_pattern}(.*?){end_pattern}"
        match = re.search(full_regex, text, re.DOTALL)
        
        if match:
            body = stylize_body(match.group(1).strip(), fal_category)
            months_data[m_name] = f"{m_emoji} متولدین {m_name}:\n{body}"
        else:
            months_data[m_name] = f"{m_emoji} متولدین {m_name}:\nاطلاعات در دسترس نیست."

    groups = [
        ["فروردین", "اردیبهشت", "خرداد"],
        ["تیر", "مرداد", "شهریور"],
        ["مهر", "آبان", "آذر"],
        ["دی", "بهمن", "اسفند"]
    ]
    
    for grp in groups:
        box_text = f"🗓 {clean_title}\n\n"
        box_text += "\n\n—————————————————————\n\n".join([months_data[m] for m in grp if m in months_data])
        box_text += SIGNATURE
        send_telegram(f"```text\n{box_text}\n```")

def main():
    links = get_links()
    if links["hafez"]:
        process_post(links["hafez"], "hafez", "فال حافظ امروز")
    if links["abjad"]:
        process_post(links["abjad"], "abjad", "فال ابجد امروز")
    if links["coffee"]:
        process_post(links["coffee"], "coffee", "فال قهوه امروز")

if __name__ == "__main__":
    main()
