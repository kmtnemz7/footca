import os
import asyncio
import re
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError, RPCError

# Ensure /tmp directory
log_dir = "/tmp"
os.makedirs(log_dir, exist_ok=True)
log_file = "/tmp/log.txt"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Log environment variables
logger.info(f"API_ID set: {'API_ID' in os.environ}")
logger.info(f"API_HASH set: {'API_HASH' in os.environ}")
logger.info(f"PHONE_NUMBER set: {'PHONE_NUMBER' in os.environ}")
logger.info(f"PASSWORD set: {'PASSWORD' in os.environ}")

api_id = os.getenv("API_ID", "24066461")
api_hash = os.getenv("API_HASH", "04d2e7ce7a20d9737960e6a69b736b4a")
phone_number = os.getenv("PHONE_NUMBER")
chat_id = "@bitfootpings"

client = TelegramClient("/tmp/bitfoot_scraper", api_id, api_hash)

async def resolve_chat(client, chat_id):
    try:
        entity = await client.get_input_entity(chat_id)
        logger.info(f"Resolved chat: {chat_id}")
        return entity
    except ValueError as e:
        logger.error(f"Failed to resolve chat {chat_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error resolving chat {chat_id}: {e}")
        return None

@client.on(events.NewMessage(chats=chat_id))
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
                with open(log_file, "a", encoding="utf-8") as f:
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
        logger.info(f"Attempting login with phone: {phone_number}")
        await client.start(phone=phone_number, password=os.getenv("PASSWORD"))
        logger.info("Client started")
        me = await client.get_me()
        logger.info(f"Authenticated as: {me.username or me.phone}")
        
        # Verify chat access
        entity = await resolve_chat(client, chat_id)
        if not entity:
            logger.error(f"Cannot proceed: Failed to access chat {chat_id}")
            return
        
        logger.info("Forwarding started: @bitfootpings → @BITFOOTCAPARSER")
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
    logger.info("Starting Bitfoot Scraper")
    asyncio.run(main())
