import requests
import time
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
CHAT_ID = "-100PUT_YOUR_CHAT_ID_HERE"

seen = {}
last_daily_ping = 0

print("Premium Pokemon monitor started...")

KEYWORDS = [
    "elite trainer box",
    "etb",
    "ultra premium collection",
    "premium collection",
    "collection box",
    "box set",
    "premium box"
]

def is_valid_product(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS)

def send(msg, image=None):

    if image:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "caption": msg,
            "parse_mode": "Markdown",
            "photo": image
        })
    else:
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
        send("🤖 Monitor running (24h check)")
        last_daily_ping = now

def check_pokemon_center():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/search?q=pokemon",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        soup = BeautifulSoup(r.text, "html.parser")

    except:
        print("PC error")
        return

    products = soup.select("a[href*='/product/']")

    for p in products:

        href = p.get("href")
        if not href:
            continue

        link = "https://www.pokemoncenter.com" + href
        title = p.get_text(strip=True)

        if not is_valid_product(title):
            continue

        if link not in seen:
            seen[link] = True

            img_tag = p.find("img")
            image = img_tag.get("src") if img_tag else None

            msg = f"""
🚨 *Pokémon Center Drop*

📦 *{title}*

🛒 [BUY NOW]({link})

#pokemon #tcg
"""

            send(msg, image)

def check_smyths():

    try:
        r = requests.get(
            "https://www.smythstoys.com/uk/en-gb/search/?text=pokemon",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        soup = BeautifulSoup(r.text, "html.parser")

    except:
        print("Smyths error")
        return

    products = soup.select("a")

    for p in products:

        href = p.get("href")
        if not href or "/product/" not in href:
            continue

        link = "https://www.smythstoys.com" + href
        title = p.get_text(strip=True)

        if not is_valid_product(title):
            continue

        if link not in seen:
            seen[link] = True

            msg = f"""
🚨 *Smyths Drop*

📦 *{title}*

🛒 {link}
"""

            send(msg)

def check_argos():

    try:
        r = requests.get(
            "https://www.argos.co.uk/search/pokemon/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        soup = BeautifulSoup(r.text, "html.parser")

    except:
        print("Argos error")
        return

    products = soup.select("a")

    for p in products:

        href = p.get("href")
        if not href or "/product/" not in href:
            continue

        link = "https://www.argos.co.uk" + href
        title = p.get_text(strip=True)

        if not is_valid_product(title):
            continue

        if link not in seen:
            seen[link] = True

            msg = f"""
🚨 *Argos Drop*

📦 *{title}*

🛒 {link}
"""

            send(msg)

while True:

    try:
        check_pokemon_center()
        check_smyths()
        check_argos()
        daily_ping()

        time.sleep(random.uniform(2, 4))

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
