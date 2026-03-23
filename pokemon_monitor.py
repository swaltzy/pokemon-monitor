import requests
import time
import random

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = set()
last_daily_ping = 0

print("Pokemon Center monitor (API) started...")

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

def check_pokemon_center():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/api/search",
            params={
                "q": "pokemon",
                "format": "json"
            },
            timeout=10
        )

        data = r.json()

    except Exception as e:
        print("PC API error:", e)
        return

    for product in data.get("results", []):

        title = product.get("name", "").lower()
        url_path = product.get("url", "")

        if not url_path:
            continue

        link = "https://www.pokemoncenter.com" + url_path

        # FILTER (ETBs + BOXES ONLY)
        if not any(keyword in title for keyword in [
            "elite trainer box",
            "etb",
            "collection",
            "premium box",
            "ultra premium"
        ]):
            continue

        if link not in seen:
            seen.add(link)

            msg = f"""
🚨 *Pokémon Center Drop*

📦 *{title.title()}*

🛒 [BUY NOW]({link})

#pokemon #tcg
"""

            print(msg)
            send(msg)

while True:

    try:
        check_pokemon_center()
        daily_ping()

        time.sleep(random.uniform(5, 10))

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
