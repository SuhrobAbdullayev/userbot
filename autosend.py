import time
from datetime import datetime

from config import ADMIN_USER_ID, TABLE_NAME, REMINDER30, REMINDER50, REMINDER70, REMINDER90, REMINDER180, REMINDER365
from db import (
    get_active_admin_task, get_users_to_send, deactivate_admin_task,
    update_sent, get_inactive_users, update_reminder, get_layal_users, delete_user
)

def send_admin_task(app):
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
        except:
            delete_user(TABLE_NAME, user_id)

    app.send_message(ADMIN_USER_ID, f"✅ Finished sending to {sent} users from {tablename}.")
    deactivate_admin_task(tablename)


def send_reminders(app):
    now = datetime.now()
    if not (9 <= now.hour < 16):
        return

    levels = [
        (30, 0, f"{REMINDER30}"),
        (50, 1, f"{REMINDER50}"),
        (70, 2, f"{REMINDER70}")
    ]

    for days, reminder_level, message_text in levels:
        inactive_users = get_inactive_users(TABLE_NAME, days, reminder_level)
        if not inactive_users:
            continue

        for user_id in inactive_users:
            try:
                app.send_message(chat_id=user_id, text=message_text)
                update_reminder(TABLE_NAME, user_id, reminder_level + 1)
                time.sleep(5)
            except:
                delete_user(TABLE_NAME, user_id)


def send_prize(app):
    now = datetime.now()
    if not (9 <= now.hour < 16):
        return

    levels = [
        (90, 3, f"{REMINDER90}"),
        (180, 4, f"{REMINDER180}"),
        (365, 5, f"{REMINDER365}")
    ]

    for days, reminder_level, message_text in levels:
        loyal_users = get_layal_users(TABLE_NAME, days, reminder_level)
        if not loyal_users:
            continue

        for user_id in loyal_users:
            try:
                app.send_message(chat_id=user_id, text=message_text)
                update_reminder(TABLE_NAME, user_id, reminder_level + 1)
                time.sleep(5)
            except:
                delete_user(TABLE_NAME, user_id)
