import requests
import time
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = {}
last_daily_ping = 0

print("Pokemon Center ULTIMATE monitor started...")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-GB,en;q=0.9"
}

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

def daily_ping():
    global last_daily_ping
    now = time.time()

    if now - last_daily_ping > 86400:
        send("🤖 Pokémon Monitor Active — 24h Status Check ✅")
        last_daily_ping = now

# 🔥 REAL STOCK CHECK
def is_in_stock(link):

    try:
        r = requests.get(link, headers=HEADERS, timeout=10)
        text = r.text.lower()

        # Detect real stock signals
        if "add to cart" in text or "in stock" in text:
            return True

        if "sold out" in text or "out of stock" in text:
            return False

        return False

    except:
        return False

def check_pokemon_center():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/api/search",
            params={"q": "pokemon", "format": "json"},
            timeout=10
        )

        data = r.json()

    except Exception as e:
        print("API error:", e)
        return

    for product in data.get("results", []):

        title = product.get("name", "").lower()
        url_path = product.get("url", "")

        if not url_path:
            continue

        link = "https://www.pokemoncenter.com" + url_path

        # FILTER
        if not any(k in title for k in [
            "elite trainer box",
            "etb",
            "collection",
            "premium box",
            "ultra premium"
        ]):
            continue

        # 🔥 REAL STOCK CHECK
        in_stock = is_in_stock(link)

        # FIRST TIME
        if link not in seen:
            seen[link] = in_stock

            if in_stock:
                msg = f"""
🚨 *NEW DROP*

📦 *{title.title()}*

🛒 [BUY NOW]({link})
"""
                print(msg)
                send(msg)

        # RESTOCK
        else:
            previous = seen[link]

            if not previous and in_stock:
                seen[link] = True

                msg = f"""
♻️ *RESTOCK DETECTED*

📦 *{title.title()}*

🛒 [BUY NOW]({link})
"""
                print(msg)
                send(msg)

            elif previous and not in_stock:
                seen[link] = False

while True:

    try:
        check_pokemon_center()
        daily_ping()

        time.sleep(random.uniform(6, 12))  # safer timing

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
