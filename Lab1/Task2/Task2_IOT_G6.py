import urequests as requests
import time

BOT_TOKEN = "8231699710:AAF01UR3dkMPL7d0NuW7ou9Z2jonBTkeCeM"
API_URL = "https://api.telegram.org/bot" + BOT_TOKEN

last_update_id = 0


def get_updates():
    global last_update_id
    url = API_URL + "/getUpdates?timeout=30&offset={}".format(last_update_id + 1)
    r = requests.get(url)
    data = r.json()
    r.close()
    return data


def send_message(update):
    message = update.get("message")
    if not message:
        return

    chat = message["chat"]
    chat_title = chat.get("title", "Private Chat")

    # Print text messages
    if "text" in message:
        user = message["from"].get("username", "unknown")
        text = message["text"]

        print("📩 [{}] @{}: {}".format(chat_title, user, text))

    # Print join events
    if "new_chat_members" in message:
        for member in message["new_chat_members"]:
            print("➕ New member joined:", member.get("first_name"))


def main():
    global last_update_id

    print("📡 Listening for Telegram messages...")

    while True:
        try:
            updates = get_updates()
            for update in updates["result"]:
                last_update_id = update["update_id"]
                send_message(update)
        except Exception as e:
            print("Error:", e)

        time.sleep(1)


main()