import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = {}
last_daily_ping = 0

print("Pokemon Center PRO monitor started...")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.pokemoncenter.com/",
    "Accept-Language": "en-GB,en;q=0.9"
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
        r = requests.get(link, headers=HEADERS, timeout=10)
        text = r.text.lower()

        if "add to cart" in text or "in stock" in text:
            return True
        if "sold out" in text or "out of stock" in text:
            return False

        return False
    except:
        return False

def fetch_products():

    for _ in range(3):  # retry system
        try:
            r = requests.get(
                "https://www.pokemoncenter.com/api/search",
                params={"q": "pokemon", "format": "json"},
                headers=HEADERS,
                timeout=10
            )

            if r.status_code != 200:
                print("API blocked:", r.status_code)
                time.sleep(2)
                continue

            return r.json()

        except Exception as e:
            print("API retry:", e)
            time.sleep(2)

    return None

def process_product(product):

    title = product.get("name", "").lower()
    url_path = product.get("url", "")

    if not url_path or not is_valid(title):
        return

    link = "https://www.pokemoncenter.com" + url_path

    in_stock = is_in_stock(link)

    # NEW PRODUCT
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

    # RESTOCK
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

def check_all():

    data = fetch_products()

    if not data:
        print("No data received")
        return

    products = data.get("results", [])

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_product, products)

while True:

    try:
        check_all()
        daily_ping()

        time.sleep(random.uniform(6, 10))

    except Exception as e:
        print("Main error:", e)
        time.sleep(15)
