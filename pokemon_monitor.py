import requests
import time

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

print("Pokemon Center ETB monitor started...")

API = "https://www.pokemoncenter.com/api/search"

seen = set()

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def check():
    params = {
        "q": "elite trainer box",
        "format": "json"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(API, params=params, headers=headers)

    try:
        data = r.json()
    except:
        print("API returned invalid response, retrying...")
        return

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
