from telethon import TelegramClient, events
from datetime import datetime

api_id = 123456     # 🔁 Your API ID
api_hash = 'your_api_hash'  # 🔁 Your API Hash
session_name = 'userbot'

client = TelegramClient(session_name, api_id, api_hash)

# ✅ OWNER + ADMINS who can control the bot
ADMINS = [123456789, 987654321]  # 🔁 Add your Telegram user IDs

# ✅ Broadcast target chat/group IDs
broadcast_targets = [-1001234567890, -1009876543210]  # 🔁 Your group IDs

# ✅ GBAN List (in-memory set; use MongoDB or file for persistence)
gban_list = set()

# 📢 Broadcast Handler
@client.on(events.NewMessage(pattern='/broadcast (.+)'))
async def broadcast_handler(event):
    sender = await event.get_sender()
    if sender.id not in ADMINS:
        return

    msg = event.pattern_match.group(1)
    success = 0
    fail = 0

    for chat_id in broadcast_targets:
        try:
            await client.send_message(chat_id, msg)
            success += 1
        except:
            fail += 1

    await event.reply(f"📣 Broadcast Completed:\n✅ Sent: {success}\n❌ Failed: {fail}")

# 🚫 GBAN Command
@client.on(events.NewMessage(pattern='/gban ?(.*)'))
async def gban_handler(event):
    sender = await event.get_sender()
    if sender.id not in ADMINS:
        return

    target = await event.get_reply_message()
    if not target:
        return await event.reply("⚠️ Reply to a user to gban them.")
    
    user = await target.get_sender()
    gban_list.add(user.id)

    for chat_id in broadcast_targets:
        try:
            await client.kick_participant(chat_id, user.id)
        except:
            continue

    await event.reply(f"🚫 GBANNED `{user.first_name}` from all groups.")

# ✅ UNGBAN Command
@client.on(events.NewMessage(pattern='/ungban ?(.*)'))
async def ungban_handler(event):
    sender = await event.get_sender()
    if sender.id not in ADMINS:
        return

    target = await event.get_reply_message()
    if not target:
        return await event.reply("⚠️ Reply to user to ungban.")

    user = await target.get_sender()
    gban_list.discard(user.id)

    await event.reply(f"✅ Removed `{user.first_name}` from GBAN list.")

# 🟢 User Join Monitor (Send info)
@client.on(events.ChatAction)
async def join_handler(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        name = user.first_name + (f" {user.last_name}" if user.last_name else "")
        username = f"@{user.username}" if user.username else "N/A"
        user_id = user.id
        time_now = datetime.now().strftime("%d %b %Y, %I:%M %p")

        # Auto-kick if in GBAN
        if user_id in gban_list:
            try:
                await client.kick_participant(event.chat_id, user_id)
                return
            except:
                pass

        await client.send_message(event.chat_id,
            f"🟢 [User Joined]\n"
            f"👤 Name: {name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: {user_id}\n"
            f"🕒 Time: {time_now}"
        )

client.start()
print("✅ UserBot Running with Join Detection, GBAN, Broadcast")
client.run_until_disconnected()
