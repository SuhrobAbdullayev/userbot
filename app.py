import threading
import time
from datetime import datetime, timedelta
from time import sleep

import schedule
from pyrogram import Client, filters
from pyrogram.types import Message

from autosend import send_admin_task, send_reminders, send_prize
from config import (
    TABLE_NAME, CHANNEL_ID, NARX_ID,
    ADMIN_USER_ID, ANKETA, ADMINS, GREETING_MESSAGE, CLIENT_BASE, AFTER_NARX
)
from db import get_user, update_last_sent, insert_user

app = Client("User", 20690773, "fdbb355357cb0d625ba1c8790e05ffad")

@app.on_message(filters.private & filters.outgoing)
def sent_message_handler(client, message):
    recipient_id = message.chat.id
    if recipient_id in ADMINS or message.chat.type == "bot":
        return
    user = get_user(TABLE_NAME, recipient_id)
    if user:
        update_last_sent(TABLE_NAME, recipient_id)
    else:
        other = get_user(f"{TABLE_NAME}_users", recipient_id)
        if other:
            update_last_sent(f"{TABLE_NAME}_users", recipient_id)
        else:
            insert_user(f"{TABLE_NAME}_users", recipient_id)

    if message.text:
        text = message.text.strip().lower()
        if text == "222":
            try:
                client.copy_message(
                    chat_id=recipient_id,
                    from_chat_id=CHANNEL_ID,
                    message_id=NARX_ID
                )
                if not user:
                    message.reply_text(AFTER_NARX)
            except Exception as e:
                client.send_message(ADMIN_USER_ID, "❌ Xato yuz berdi: " + str(e))
                print(e)
            if recipient_id == ADMIN_USER_ID:
                message.delete()
        elif text == "111":
            message.reply_text(ANKETA)
            message.delete()
        elif text == "333":
            message.reply_text(CLIENT_BASE)
            message.delete()

@app.on_message(filters.private)
def handle_message(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in ADMINS or message.chat.type == "bot":
        return
    if user_id == ADMIN_USER_ID:
        pass
    else:
        user = get_user(TABLE_NAME, user_id)
        now = datetime.now()

        if user:
            last_sent = user.get("last_sent")
            update_last_sent(TABLE_NAME, user_id)
            if last_sent and now - last_sent >= timedelta(days=5):
                message.reply_text("🤗 Assalomu Aleykum. Siz bizning mijozlar royxatimizda borsiz.\nMenga habaringiz bo'lsa yozib qoldiring.")
        else:
            other = get_user(f"{TABLE_NAME}_users", user_id)
            if other:
                last_sent = other.get("last_sent")
                update_last_sent(f"{TABLE_NAME}_users", user_id)
                if last_sent and now - last_sent >= timedelta(days=3):
                    message.reply_text("🤗 Assalomu Aleykum.\nMenga habaringiz bo'lsa yozib qoldiring.")
                    sleep(3)
                    message.reply_text(GREETING_MESSAGE)
            else:
                message.reply_text("🤗 Assalomu Aleykum.\nMenga habaringiz bo'lsa yozib qoldiring.")
                sleep(3)
                message.reply_text(GREETING_MESSAGE)
                insert_user(f"{TABLE_NAME}_users", user_id)

    if message.text:
        user = get_user(TABLE_NAME, user_id)
        text = message.text.strip().lower()
        if "narx" in text or "нарх" in text or text == "222":
            try:
                client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=CHANNEL_ID,
                    message_id=NARX_ID
                )
                if not user:
                    message.reply_text(AFTER_NARX)
            except Exception as e:
                client.send_message(ADMIN_USER_ID, "❌ Xato yuz berdi: " + str(e))
                print(e)
            if user_id == ADMIN_USER_ID:
                message.delete()
        elif text == "111" or text == "anketa":
            message.reply_text(ANKETA)
            if user_id == ADMIN_USER_ID:
                message.delete()
        elif text == "333":
            message.reply_text(CLIENT_BASE)
            if user_id == ADMIN_USER_ID:
                message.delete()


def setup_schedules():
    schedule.every(5).minutes.do(lambda: send_admin_task(app))
    schedule.every(60).minutes.do(lambda: send_reminders(app))
    schedule.every(60).minutes.do(lambda: send_prize(app))


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("✅ Bot started.")
    setup_schedules()
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    app.run()
