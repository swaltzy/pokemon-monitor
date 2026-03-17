import requests
import time
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "-1003851579025"

seen = {}
last_daily_ping = 0

print("Multi-site Pokemon monitor started...")

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
        send("🤖 Monitor still running (24h check)")
        last_daily_ping = now

# ----------------------
# POKEMON CENTER
# ----------------------

def check_pokemon_center():

    try:
        r = requests.get(
            "https://www.pokemoncenter.com/search?q=elite+trainer+box",
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

        if "trainer box" in title.lower() or "etb" in title.lower():

            if link not in seen:
                seen[link] = True

                msg = f"""
🚨 *Pokémon Center Drop*

📦 {title}

🛒 {link}
"""
                send(msg)

# ----------------------
# SMYTHS
# ----------------------

def check_smyths():

    try:
        r = requests.get(
            "https://www.smythstoys.com/uk/en-gb/search/?text=pokemon+elite+trainer+box",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        soup = BeautifulSoup(r.text, "html.parser")

    except:
        print("Smyths error")
        return

    products = soup.select("a[href*='/product/']")

    for p in products:

        href = p.get("href")
        if not href:
            continue

        link = "https://www.smythstoys.com" + href
        title = p.get_text(strip=True)

        if "pokemon" in title.lower():

            if link not in seen:
                seen[link] = True

                msg = f"""
🚨 *SMYTHS DROP*

📦 {title}

🛒 {link}
"""
                send(msg)

# ----------------------
# ARGOS
# ----------------------

def check_argos():

    try:
        r = requests.get(
            "https://www.argos.co.uk/search/pokemon-elite-trainer-box/",
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

        if "pokemon" in title.lower():

            if link not in seen:
                seen[link] = True

                msg = f"""
🚨 *ARGOS DROP*

📦 {title}

🛒 {link}
"""
                send(msg)

# ----------------------
# LOOP
# ----------------------

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
