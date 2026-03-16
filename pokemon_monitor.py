import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "8262077424"

URL = "https://www.pokemoncenter.com/search?q=elite+trainer+box"

seen = set()

print("Pokemon Center ETB monitor started...")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
send("✅ BOT TEST SUCCESS — Telegram alerts working")
def check():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    products = soup.select("a.product-card")

    for p in products:

        link = "https://www.pokemoncenter.com" + p.get("href")
        title = p.text.lower()

        if "elite trainer box" in title or "etb" in title:

            if link not in seen:

                seen.add(link)

                msg = f"🚨 ETB DROP DETECTED\n\n{title}\n{link}"

                print(msg)

                send(msg)


while True:

    try:
        check()
        time.sleep(10)

    except Exception as e:

        print("Error:", e)

        time.sleep(20)
