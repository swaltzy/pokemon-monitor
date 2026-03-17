import requests
import time
import random
from bs4 import BeautifulSoup

# CONFIG

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = {}
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

# DAILY STATUS

def daily_ping():
    global last_daily_ping
    now = time.time()

    if now - last_daily_ping > 86400:
        send("🤖 ETB Monitor still running (24h status check)")
        last_daily_ping = now

# CHECK PRODUCTS

def check():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/search?q=elite+trainer+box",
            headers=headers,
            timeout=5
        )

        soup = BeautifulSoup(r.text, "html.parser")

    except:
        print("Page error, retrying...")
        return

    products = soup.select("a[href*='/product/']")

    for p in products:

        href = p.get("href")
        if not href:
            continue

        link = "https://www.pokemoncenter.com" + href
        title = p.get_text(strip=True).lower()

        if "trainer box" not in title and "etb" not in title:
            continue

        # detect stock from text
        text = p.get_text().lower()

        in_stock = True
        if "out of stock" in text or "sold out" in text:
            in_stock = False

        # FIRST TIME SEEING PRODUCT
        if link not in seen:
            seen[link] = in_stock

            if in_stock:
                msg = f"""
🚨 *NEW ETB DETECTED*

📦 *Product:* {title.title()}

🛒 [BUY NOW]({link})
"""
                print(msg)
                send(msg)

        # RESTOCK DETECTION
        else:
            previous_stock = seen[link]

            if not previous_stock and in_stock:
                seen[link] = True

                msg = f"""
♻️ *ETB RESTOCK DETECTED*

📦 *Product:* {title.title()}

🛒 [BUY NOW]({link})
"""
                print(msg)
                send(msg)

            elif previous_stock and not in_stock:
                seen[link] = False

# LOOP

while True:

    try:
        check()
        daily_ping()
        time.sleep(random.uniform(2, 4))

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
