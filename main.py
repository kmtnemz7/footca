import os
from telethon import TelegramClient, events
from flask import Flask
import threading
import asyncio
import re

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')

client = TelegramClient("bitfoot_scraper", api_id, api_hash)

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
        
        # Extract all Solana contract addresses
        contracts = re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', msg_text)
        
        # Remove duplicates while preserving order
        unique_contracts = list(dict.fromkeys(contracts))
        
        if unique_contracts:
            for contract in unique_contracts:
                await client.send_message("BITFOOTCAPARSER", f"CA Detected:\n`{contract}`")
                print(f"✅ Sent contract: {contract}")
                
                # Save to log file
                try:
                    with open("log.txt", "a", encoding="utf-8") as f:
                        f.write(
                            f"\n[{msg.date}] From: {msg.chat.username or msg.chat.id} → Contract: {contract}\n"
                        )
                except Exception as e:
                    print(f"❌ Logging error: {e}")
            print("-" * 40)
        else:
            print("❌ Skipped: No Solana address found.\n" + "-" * 40)
    except Exception as e:
        print(f"❌ Error processing message: {e}")
#_____LOGGING PHANES IN .TXT

@client.on(events.NewMessage(chats="BITFOOTCAPARSER"))
async def log_clean_token_stats(event):
    msg_text = event.raw_text

    # Check that the message includes both headers
    if "📊 Token Stats" in msg_text and "🔒 Security" in msg_text:
        try:
            # Extract only the relevant lines from the message
            lines = msg_text.splitlines()
            capture = False
            filtered_lines = []

            for line in lines:
                # Start capturing after this line
                if line.startswith("📊 Token Stats"):
                    capture = True

                if capture:
                    # Stop capturing if we hit a new section or empty
                    if line.strip() == "":
                        break
                    # Remove markdown-like formatting (e.g., [text](link))
                    clean_line = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line)
                    filtered_lines.append(clean_line)

            # Save clean output
            clean_output = "\n".join(filtered_lines)
            with open("phanes_stats_log.txt", "a", encoding="utf-8") as f:
                f.write("\n--- New Token Stats ---\n")
                f.write(clean_output + "\n")
                f.write("-" * 40 + "\n")
            print("📥 Logged cleaned Phanes stats.")
        
        except Exception as e:
            print(f"❌ Logging error: {e}")



# === Flask for keep-alive ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bitfoot bot is alive!"

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running"}

def run_flask():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# === Async main ===
async def main():
    try:
        await client.start(phone=phone_number)
        print("📡 Forwarding started: @bitfootpings → @BITFOOTCAPARSER")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Bot error: {e}")

# === Start Flask + Telethon ===
if __name__ == "__main__":
    print("🚀 Starting Bitfoot Telegram Bot...")
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
