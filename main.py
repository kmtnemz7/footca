import os
from telethon import TelegramClient, events
import asyncio

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')
client = TelegramClient("bitfoot_scraper", api_id, api_hash)

@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    try:
        msg = event.message
        text = msg.raw_text

        if not text or "🔎" not in text:
            return

        # Cut message at the first occurrence of 🔎
        trimmed = text.split("🔎")[0].strip()

        if trimmed:
            await client.send_message("BACKENDZEROPINGxc_vy", trimmed, parse_mode="Markdown")
    except Exception as e:
        pass

#Filter and send back PHANES MESSAGES

@client.on(events.NewMessage(chats="BACKENDZEROPINGxc_vy"))
async def handle(event):
    msg = event.message
    if not msg or not msg.text:
        return

    full_text = msg.text

    if "DEF" in full_text:
        cutoff_index = full_text.find("DEF")
        trimmed_text = full_text[:cutoff_index].strip()

        safe_entities = [
            e for e in msg.entities or []
            if e.offset < cutoff_index
        ]

        await client.send_message(
            "zeropingphane",
            trimmed_text,
            formatting_entities=safe_entities
        )

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
