import os
from telethon import TelegramClient, events
import asyncio

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')
client = TelegramClient("bitfoot_scraper", api_id, api_hash)
password = "AirJordan1!"

@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    try:
        msg = event.message
        text = msg.raw_text

        if not text or "🔎" not in text:
            print("⚠️ Skipped: No deep scan info.\n" + "-" * 40)
            return

        # Cut message at the first occurrence of 🔎
        trimmed = text.split("🔎")[0].strip()

        if trimmed:
            await client.send_message("BACKENDZEROPINGxc_vy", trimmed, parse_mode="Markdown")
            print("✅ Forwarded trimmed message\n" + "-" * 40)
        else:
            print("⚠️ Skipped: Trimmed message was empty\n" + "-" * 40)

    except Exception as e:
        print(f"❌ Error processing message: {e}")

# === Async main ===
async def main():
    try:
        await client.start(phone=phone_number)
        print("📡 Scraper started: @bitfootpings → @BACKENDZEROPINGxc_vy")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Bitfoot Scraper...")
    asyncio.run(main())
