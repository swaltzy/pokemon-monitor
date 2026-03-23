import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = {}
last_daily_ping = 0

print("Pokemon Center FAST monitor started...")

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

def is_valid(title):
    return any(k in title for k in [
        "elite trainer box",
        "etb",
        "collection",
        "premium box",
        "ultra premium"
    ])

def check_product(product):

    title = product.get("name", "").lower()
    url_path = product.get("url", "")

    if not url_path or not is_valid(title):
        return

    link = "https://www.pokemoncenter.com" + url_path

    try:
        r = requests.get(link, headers=HEADERS, timeout=8)
        text = r.text.lower()

        in_stock = "add to cart" in text or "in stock" in text

    except:
        return

    # NEW
    if link not in seen:
        seen[link] = in_stock

        if in_stock:
            msg = f"""
🚨 *NEW DROP*

📦 *{title.title()}*

🛒 [BUY NOW]({link})
"""
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
            send(msg)

        elif prev and not in_stock:
            seen[link] = False

def check_all():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/api/search",
            params={"q": "pokemon", "format": "json"},
            timeout=10
        )

        data = r.json()

    except:
        print("API error")
        return

    products = data.get("results", [])

    # 🔥 MULTI-THREADING (FAST)
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_product, products)

while True:

    try:
        check_all()
        daily_ping()

        time.sleep(random.uniform(4, 7))  # faster loop

    except Exception as e:
        print("Error:", e)
        time.sleep(15)
