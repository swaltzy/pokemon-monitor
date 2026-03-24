import requests
import time
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = set()
last_daily_ping = 0

print("Pokemon Center HYBRID monitor started...")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS = [
    "elite trainer box",
    "etb",
    "collection",
    "premium box",
    "ultra premium"
]

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)
    except:
        pass

def daily_ping():
    global last_daily_ping
    now = time.time()

    if now - last_daily_ping > 86400:
        send("🤖 Monitor running (24h check)")
        last_daily_ping = now

def is_valid(title):
    return any(k in title for k in KEYWORDS)

# 🔥 FALLBACK SCRAPER (Google)
def google_fallback():
    try:
        query = "pokemon elite trainer box site:pokemoncenter.com"
        url = f"https://www.google.com/search?q={query}"

        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.select("a")

        for a in links:
            href = a.get("href", "")

            if "/url?q=" in href and "pokemoncenter.com" in href:
                link = href.split("/url?q=")[1].split("&")[0]

                if link not in seen:
                    seen.add(link)

                    msg = f"""
🚨 *DROP DETECTED (Fallback)*

🛒 {link}
"""
                    print("Fallback found:", link)
                    send(msg)

    except:
        print("Fallback error")

def fetch_api():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/api/search",
            params={"q": "pokemon", "format": "json"},
            headers=HEADERS,
            timeout=10
        )

        if r.status_code != 200:
            return None

        return r.json()

    except:
        return None

def check():

    data = fetch_api()

    # 🔥 IF BLOCKED → USE FALLBACK
    if not data:
        print("API blocked → using fallback")
        google_fallback()
        return

    for product in data.get("results", []):

        title = product.get("name", "").lower()
        url_path = product.get("url", "")

        if not url_path:
            continue

        link = "https://www.pokemoncenter.com" + url_path

        if not is_valid(title):
            continue

        if link not in seen:
            seen.add(link)

            msg = f"""
🚨 *Pokémon Center Drop*

📦 *{title.title()}*

🛒 {link}
"""
            print("Found:", title)
            send(msg)

while True:

    try:
        check()
        daily_ping()

        time.sleep(random.uniform(12, 20))

    except Exception as e:
        print("Error:", e)
        time.sleep(30)
