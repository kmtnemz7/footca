import os
import asyncio
import re
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
client = TelegramClient("bitfoot_scraper", api_id, api_hash)

@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    logging.info("Event handler triggered")
    try:
        msg = event.message
        msg_text = msg.raw_text
        
        logging.info(f"NEW MESSAGE | Time: {msg.date} | From: {msg.chat.username or msg.chat.id} | Content: {msg.text if msg.text else '[Non-text content]'}")
        
        # Extract Solana contract addresses
        contracts = re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', msg_text)
        unique_contracts = list(dict.fromkeys(contracts))
        
        if unique_contracts:
            for contract in unique_contracts:
                await client.send_message("BITFOOTCAPARSER", f"CA Detected:\n`{contract}`")
                logging.info(f"Sent contract: {contract}")
                
                # Save to log file
                try:
                    with open("log.txt", "a", encoding="utf-8") as f:
                        f.write(f"\n[{msg.date}] From: {msg.chat.username or msg.chat.id} → Contract: {contract}\n")
                except Exception as e:
                    logging.error(f"Logging error: {e}")
        else:
            logging.info("Skipped: No Solana address found.")
    except FloodWaitError as e:
        logging.error(f"FloodWaitError: Waiting for {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logging.error(f"Error processing message: {e}", exc_info=True)

async def main():
    try:
        logging.info("Starting Telegram client...")
        await client.start(phone=phone)
        logging.info("Forwarding started: @bitfootpings → @BITFOOTCAPARSER")
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"Bot error: {e}", exc_info=True)

if __name__ == "__main__":
    logging.info("Starting Bitfoot Telegram Bot...")
    asyncio.run(main())
