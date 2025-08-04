import os, asyncio, re
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

api_id     = int(os.getenv("API_ID"))
api_hash   = os.getenv("API_HASH")
bot_token  = os.getenv("BOT_TOKEN")

SOURCE_GROUP  = os.getenv("BACKEND_GROUP",  "BACKENDZEROPINGxc_vy")
TARGET_GROUP  = os.getenv("FRONTEND_GROUP", "ZeroPingX")

bot = TelegramClient("zeroping_bot", api_id, api_hash)


@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay(event):
    try:
        msg = event.message

        # Re-send EXACTLY what arrived, with original entities → formatting kept
        await bot.send_message(
            entity = TARGET_GROUP,
            message = msg.text or msg.raw_text or "",
            formatting_entities = msg.entities if msg.entities else None,
            file = msg.media if msg.media else None,
            link_preview = False               # ⛔ hide site previews
        )

    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await relay(event)                     # retry once after wait
    except Exception as e:
        print("❌ BOT FORWARD ERROR:", e)


async def main():
    await bot.start(bot_token=bot_token)
    print(f"Listening in {SOURCE_GROUP} → relaying to {TARGET_GROUP}")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
