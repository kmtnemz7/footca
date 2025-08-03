import os
from telethon import TelegramClient, events
import asyncio
import re

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')
client = TelegramClient("bitfoot_scraper", api_id, api_hash)
password = "AirJordan1!"

# === Logging + Forwarding ===
@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    try:
        msg = event.message
        msg_text = msg.raw_text

        print("🟢 NEW MESSAGE")
        print(f"📅 Time: {msg.date}")
        print(f"📨 From: {msg.chat.username or msg.chat.id}")
        print(f"📦 Type: {'Text' if msg.text else 'Non-text'}")
        print(f"📝 Content: {msg.text if msg.text else '[Non-text content]'}")

        # Extract Solana contract addresses
        contracts = re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', msg_text)
        unique_contracts = list(dict.fromkeys(contracts))

        # Detect if message includes a token summary block
        has_token_summary = msg_text.startswith("💊") and "solscan.io/token" in msg_text

        # Build the message to send
        message_to_send = ""

        if unique_contracts:
            for contract in unique_contracts:
                message_to_send += f"✅ **CA Detected:**\n\n`{contract}`\n\n"

        if has_token_summary:
            # Format the whole block as a monospaced markdown section
            message_to_send += f"```{msg_text}```"

        if message_to_send:
            await client.send_message("BACKENDZEROPINGxc_vy", message_to_send, parse_mode="markdown")
            print("✅ Forwarded contract & token summary\n" + "-" * 40)
        else:
            print("❌ Skipped: No valid CA or summary block.\n" + "-" * 40)

    except Exception as e:
        print(f"❌ Error processing message: {e}")

# === Async main ===
async def main():
    try:
        await client.start(phone=phone_number)
        print("📡 Forwarding started: @bitfootpings → @BACKENDZEROPINGxc_vy")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Bot error: {e}")

# === Start Telethon ===
if __name__ == "__main__":
    print("🚀 Starting Bitfoot Telegram Bot...")
    asyncio.run(main())
