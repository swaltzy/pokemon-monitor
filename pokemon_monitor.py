import requests
import time
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID = "-100..."

URL = "https://www.pokemoncenter.com/search?q=elite+trainer+box"

seen = set()
last_daily_ping = 0

print("Pokemon Center ETB monitor started...")


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
        send("🤖 ETB Monitor still running (24h status check)")
        last_daily_ping = now


def check():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")

    products = soup.select("a[href*='/product/']")

    for p in products:

        href = p.get("href")
        if not href:
            continue

        link = "https://www.pokemoncenter.com" + href
        title = p.get_text(strip=True).lower()

        if "elite trainer box" in title or "etb" in title:

            if link not in seen:
                seen.add(link)

                msg = f"""
🚨 *Pokémon Center Drop Detected*

📦 *Product:* {title.title()}

🛒 *Buy Now:*  
{link}

#pokemon #tcg #etb
"""

                print(msg)
                send(msg)


while True:

    try:
        check()
        daily_ping()
        time.sleep(random.uniform(2, 4))

    except Exception as e:

        print("Error:", e)
        time.sleep(20)
