import requests
import time
import random

# CONFIG

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

API_URL = "https://www.pokemoncenter.com/api/search"

seen = set()
last_daily_ping = 0

print("Pokemon Center ETB monitor started...")

# SEND MESSAGE

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

# DAILY STATUS PING

def daily_ping():
    global last_daily_ping
    now = time.time()

    if now - last_daily_ping > 86400:
        send("🤖 ETB Monitor still running (24h status check)")
        last_daily_ping = now

# MAIN CHECK

def check():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "q": "pokemon",
        "format": "json"
    }

    try:
        r = requests.get(API_URL, params=params, headers=headers, timeout=5)
        data = r.json()

    except:
        print("API error, retrying...")
        return

    for product in data.get("results", []):

        title = product.get("name", "").lower()
        url_path = product.get("url", "")

        if not url_path:
            continue

        link = "https://www.pokemoncenter.com" + url_path

        if "trainer box" in title or "etb" in title:

            if link not in seen:
                seen.add(link)

                msg = f"""
🚨 *Pokémon Center Drop Detected*

📦 *Product:* {title.title()}

🛒 [CLICK HERE TO BUY]({link})

#pokemon #tcg #etb
"""

                print(msg)
                send(msg)

# LOOP

while True:

    try:
        check()
        daily_ping()
        time.sleep(random.uniform(2, 4))

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
