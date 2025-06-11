import time
from datetime import datetime

from config import ADMIN_USER_ID, TABLE_NAME
from db import (
    get_active_admin_task, get_users_to_send, deactivate_admin_task,
    update_sent, get_inactive_users, update_reminder, get_layal_users
)

def send_admin_task(app):
    print("test task")
    now = datetime.now()
    if not (9 <= now.hour < 24):
        return

    task = get_active_admin_task()
    if not task:
        return

    channel_id, message_id, count, tablename = task[1], task[2], task[3], task[4]
    user_ids = get_users_to_send(tablename, count)
    if not user_ids:
        app.send_message(ADMIN_USER_ID, "❌ No users to send messages to.")
        deactivate_admin_task(tablename)
        return

    sent = 0
    for user_id in user_ids:
        try:
            app.copy_message(chat_id=user_id, from_chat_id=channel_id, message_id=message_id)
            update_sent(tablename, user_id)
            sent += 1
            time.sleep(5)
        except Exception as e:
            print(f"❌ Failed to send to {user_id}: {e}")

    app.send_message(ADMIN_USER_ID, f"✅ Finished sending to {sent} users from {tablename}.")
    deactivate_admin_task(tablename)


def send_reminders(app):
    now = datetime.now()
    if not (1 <= now.hour < 24):
        return

    levels = [
        (20, 0, "❗20 kun davomida siz bilan aloqa bo‘lmadi."),
        (40, 1, "❗️40 kun davomida siz bilan aloqa bo‘lmadi."),
        (60, 2, "❗️60 kun davomida siz bilan aloqa bo‘lmadi.")
    ]

    for days, reminder_level, message_text in levels:
        inactive_users = get_inactive_users(TABLE_NAME, days, reminder_level)
        if not inactive_users:
            continue

        for user_id in inactive_users:
            try:
                update_reminder(TABLE_NAME, user_id, reminder_level + 1)
                app.send_message(chat_id=user_id, text=message_text)
                print(f"✅ Reminder level {reminder_level + 1} sent to {user_id}")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Failed to send to {user_id}: {e}")


def send_prize(app):
    now = datetime.now()
    if not (1 <= now.hour < 24):
        return

    levels = [
        (90, 3, "siz 90 kun davomida faol bo‘lmadingiz. Sizga sovg‘a taqdim etamiz."),
        (180, 4, "siz 180 kun davomida faol bo‘lmadingiz. Sizga sovg‘a taqdim etamiz."),
        (365, 5, "siz 365 kun davomida faol bo‘lmadingiz. Sizga sovg‘a taqdim etamiz.")
    ]

    for days, reminder_level, message_text in levels:
        loyal_users = get_layal_users(TABLE_NAME, days, reminder_level)
        if not loyal_users:
            continue

        for user_id in loyal_users:
            try:
                update_reminder(TABLE_NAME, user_id, reminder_level + 1)
                app.send_message(chat_id=user_id, text=message_text)
                print(f"✅ Reminder level {reminder_level + 1} sent to {user_id}")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Failed to send to {user_id}: {e}")
