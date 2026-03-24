import requests
import time
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = set()
last_daily_ping = 0

print("Pokemon Center CLEAN monitor started...")

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

def check():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/search?q=pokemon",
            headers=HEADERS,
            timeout=15
        )

        soup = BeautifulSoup(r.text, "html.parser")

    except:
        print("Blocked, retrying later...")
        time.sleep(30)
        return

    products = soup.select("a[href*='/product/']")

    for p in products:

        href = p.get("href")
        if not href:
            continue

        link = "https://www.pokemoncenter.com" + href
        title = p.get_text(strip=True).lower()

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

        time.sleep(random.uniform(15, 25))

    except Exception as e:
        print("Error:", e)
        time.sleep(30)
