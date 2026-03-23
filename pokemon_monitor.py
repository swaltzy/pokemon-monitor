import cloudscraper
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = {}
last_daily_ping = 0

print("Pokemon Center STEALTH monitor started...")

scraper = cloudscraper.create_scraper()

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
        print("Telegram error")

def daily_ping():
    global last_daily_ping
    now = time.time()

    if now - last_daily_ping > 86400:
        send("🤖 Pokémon Monitor Active — 24h Status Check ✅")
        last_daily_ping = now

def is_valid(title):
    return any(k in title for k in KEYWORDS)

def is_in_stock(link):
    try:
        r = scraper.get(link, timeout=10)
        text = r.text.lower()

        if "add to cart" in text:
            return True
        if "sold out" in text:
            return False

        return False
    except:
        return False

def fetch_products():

    try:
        r = scraper.get(
            "https://www.pokemoncenter.com/search?q=pokemon",
            timeout=10
        )

        return r.text

    except Exception as e:
        print("Scrape error:", e)
        return None

def process_page(html):

    if not html:
        return

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    products = soup.select("a[href*='/product/']")

    for p in products:

        href = p.get("href")
        if not href:
            continue

        link = "https://www.pokemoncenter.com" + href
        title = p.get_text(strip=True).lower()

        if not is_valid(title):
            continue

        in_stock = is_in_stock(link)

        if link not in seen:
            seen[link] = in_stock

            if in_stock:
                msg = f"""
🚨 *NEW DROP*

📦 *{title.title()}*

🛒 [BUY NOW]({link})
"""
                print("NEW:", title)
                send(msg)

        else:
            prev = seen[link]

            if not prev and in_stock:
                seen[link] = True

                msg = f"""
♻️ *RESTOCK DETECTED*

📦 *{title.title()}*

🛒 [BUY NOW]({link})
"""
                print("RESTOCK:", title)
                send(msg)

            elif prev and not in_stock:
                seen[link] = False

while True:

    try:
        html = fetch_products()
        process_page(html)
        daily_ping()

        time.sleep(random.uniform(6, 10))

    except Exception as e:
        print("Main error:", e)
        time.sleep(15)
