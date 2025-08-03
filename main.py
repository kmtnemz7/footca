import os
import asyncio
import re
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError, RPCError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/app/log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

api_id = os.getenv("API_ID", "24066461")
api_hash = os.getenv("API_HASH", "04d2e7ce7a20d9737960e6a69b736b4a")
phone_number = os.getenv("PHONE_NUMBER")

client = TelegramClient("bitfoot_scraper", api_id, api_hash)

@client.on(events.NewMessage(chats=["-1002389539807"]))
async def forward(event):
    try:
        msg = event.message
        msg_text = msg.raw_text
        logger.info(f"New message | Time: {msg.date} | From: {msg.chat.username or msg.chat.id} | Type: {'Text' if msg.text else 'Non-text'} | Content: {msg.text or '[Non-text]'}")
        
        contracts = re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', msg_text)
        unique_contracts = list(dict.fromkeys(contracts))
        
        if unique_contracts:
            for contract in unique_contracts:
                await client.send_message("BITFOOTCAPARSER", f"CA Detected:\n{contract}")
                logger.info(f"Sent contract: {contract}")
                with open("/app/log.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n[{msg.date}] From: {msg.chat.username or msg.chat.id} → Contract: {contract}\n")
            logger.info("-" * 40)
        else:
            logger.info("Skipped: No Solana address found")
    except FloodWaitError as e:
        logger.error(f"Flood wait: Waiting {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"Message error: {e}")

async def main():
    try:
        logger.info("Starting client")
        if not phone_number:
            logger.error("PHONE_NUMBER not set")
            return
        await client.start(phone=phone_number, password=os.getenv("PASSWORD"))
        logger.info("Client started")
        me = await client.get_me()
        logger.info(f"Authenticated as: {me.username or me.phone}")
        logger.info("Forwarding started: -1002389539807 → @BITFOOTCAPARSER")
        await client.run_until_disconnected()
    except SessionPasswordNeededError:
        logger.error("2FA required. Set PASSWORD env var")
    except FloodWaitError as e:
        logger.error(f"Flood wait: Waiting {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except RPCError as e:
        logger.error(f"Telegram error: {e}")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await client.disconnect()
        logger.info("Client disconnected")

if __name__ == "__main__":
    logger.info("Starting Bitfoot Bot")
    asyncio.run(main())
