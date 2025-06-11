@app.on_message(filters.text | filters.sticker | filters.voice | filters.animation | filters.photo)
def start(client, message):
    tablename = "fargona"
    user_id = message.from_user.id
    user = read_user_ids(user_id)

    if user:
        update_last_sent(user_id)
        client.send_message(
            message.chat.id,
            "Date is saved",
            disable_web_page_preview=True
        )
    else:
        client.send_message(
            message.chat.id,
            "you are welcome",
            disable_web_page_preview=True
        )