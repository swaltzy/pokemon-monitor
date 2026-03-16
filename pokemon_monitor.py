import requests
import time

BOT_TOKEN = "8653650833:AAGxD06P67Z7HVz6KCiePlsKvKo-SsXzH1Y"
CHAT_ID = "8262077424"

print("Pokemon Center ETB monitor started...")

API = "https://www.pokemoncenter.com/api/search"

seen = set()

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def check():
    params = {
        "q": "trainer box",
        "format": "json"
    }

    r = requests.get(API, params=params)
    data = r.json()

    for product in data.get("results", []):
        title = product["name"].lower()
        link = "https://www.pokemoncenter.com" + product["url"]

        if "trainer box" in title or "etb" in title:

            if link not in seen:
                seen.add(link)

                msg = f"🚨 ETB DROP DETECTED\n\n{product['name']}\n{link}"
                print(msg)
                send(msg)

while True:
    try:
        check()
        time.sleep(10)
    except Exception as e:
        print("Error:", e)
        time.sleep(20)