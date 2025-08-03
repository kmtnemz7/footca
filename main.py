import os
import asyncio
import re
from telethon import TelegramClient, events

api_id = 24066461
api_hash = "04d2e7ce7a20d9737960e6a69b736b4a"

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
async def print_group_id(event):
    print(f"📍 Group ID: {event.chat_id}")
# ==== Send log file ====
#async def send_log_file_periodically():
#    while True:
#        try:
#            await asyncio.sleep(6 * 60 * 60)  # Wait 6 hours
#            
#            # Send the file and capture the message object
#            sent_message = await client.send_file(
#                -1001234567890,  # Replace with your real group ID
#                "phanes_stats_log.txt",
#                caption="📦 Phanes log file (last 6 hours)"
#            )
#            print("📤 Log file sent.")
#
#            # Pin the sent message
#            await client.pin_message(-1001234567890, sent_message)
#            print("📌 Message pinned.")
#
#        except Exception as e:
#            print(f"❌ Error during log send/pin: {e}")

# === Async main ===
async def main():
    try:
        await client.start()
        print("📡 Forwarding started: @bitfootpings → @BITFOOTCAPARSER")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Bot error: {e}")

# === Start Flask + Telethon ===
if __name__ == "__main__":
    print("🚀 Starting Bitfoot Telegram Bot...")
    asyncio.run(main())
