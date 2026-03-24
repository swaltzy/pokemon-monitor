import requests
import time
import random

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = set()
last_daily_ping = 0

print("Pokemon Center STABLE monitor started...")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
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
        send("🤖 Pokémon Monitor Active — 24h Status Check ✅")
        last_daily_ping = now

def fetch_products():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/api/search",
            params={"q": "pokemon", "format": "json"},
            headers=HEADERS,
            timeout=10
        )

        if r.status_code != 200:
            print("Blocked, backing off...")
            time.sleep(20)
            return None

        return r.json()

    except:
        print("Connection issue, retrying...")
        time.sleep(15)
        return None

def check():

    data = fetch_products()

    if not data:
        return

    for product in data.get("results", []):

        title = product.get("name", "").lower()
        url_path = product.get("url", "")

        if not url_path:
            continue

        link = "https://www.pokemoncenter.com" + url_path

        if not any(k in title for k in KEYWORDS):
            continue

        if link not in seen:
            seen.add(link)

            msg = f"""
🚨 *Pokémon Center Drop*

📦 *{title.title()}*

🛒 [BUY NOW]({link})
"""
            print("Found:", title)
            send(msg)

while True:

    try:
        check()
        daily_ping()

        time.sleep(random.uniform(10, 20))  # slower = safer

    except Exception as e:
        print("Main error:", e)
        time.sleep(30)
