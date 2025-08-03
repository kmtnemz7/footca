import os
import asyncio
import re
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError, RPCError, ChatWriteForbiddenError, TypeNotFoundError

log_dir = "/tmp"
os.makedirs(log_dir, exist_ok=True)
log_file = "/tmp/log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

api_id = os.getenv("API_ID", "24066461")
api_hash = os.getenv("API_HASH", "04d2e7ce7a20d9737960e6a69b736b4a")
phone_number = os.getenv("PHONE_NUMBER", "+61404319634")
source_chat = "@bitfootpings"
target_chat = "@BITFOOTCAPARSER"
phanes_bot = "@PhanesGoldBot"

client = TelegramClient("bitfoot_scraper", api_id, api_hash)

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

async def send_log_file():
    while True:
        try:
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                await client.send_file(target_chat, log_file, caption="Phanes Responses")
                logger.info(f"Sent log file to {target_chat}")
            else:
                logger.info("Log file empty or missing, skipping send")
        except TypeNotFoundError as e:
            logger.error(f"TypeNotFoundError sending log file: {e}. Skipping.")
        except Exception as e:
            logger.error(f"Error sending log file: {e}")
        await asyncio.sleep(600)

async def status_message():
    while True:
        try:
            await client.send_message(target_chat, "🔃 Logging calls...")
            logger.info(f"Sent status message to {target_chat}")
        except ChatWriteForbiddenError:
            logger.error(f"Cannot send status message to {target_chat}: No write permission")
        except TypeNotFoundError as e:
            logger.error(f"TypeNotFoundError sending status message: {e}. Skipping.")
        except Exception as e:
            logger.error(f"Error sending status message: {e}")
        await asyncio.sleep(60)

@client.on(events.NewMessage(chats=source_chat))
async def forward(event):
    try:
        msg = event.message
        msg_text = msg.raw_text or ""
        contracts = re.findall(r'[1-9A-HJ-NP-Za-km-z]{32,44}', msg_text)
        unique_contracts = list(dict.fromkeys(contracts))
        
        if unique_contracts:
            for contract in unique_contracts:
                try:
                    await client.send_message(target_chat, f"CA Detected:\n{contract}")
                    logger.info(f"CA Detected: {contract}")
                except ChatWriteForbiddenError:
                    logger.error(f"Cannot send to {target_chat}: No write permission")
                except TypeNotFoundError as e:
                    logger.error(f"TypeNotFoundError sending contract {contract}: {e}. Skipping.")
                except Exception as e:
                    logger.error(f"Error sending contract {contract}: {e}")
    except TypeNotFoundError as e:
        logger.error(f"TypeNotFoundError processing message: {e}. Skipping.")
    except FloodWaitError as e:
        logger.error(f"Flood wait: Waiting {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"Message error: {e}")

@client.on(events.NewMessage(chats=target_chat, from_users=phanes_bot))
async def log_phanes_response(event):
    try:
        msg = event.message
        msg_text = msg.raw_text or ""
        if msg_text:
            # Extract key information using regex
            pattern = r'([\w\s]+)\s+\(\$([\w]+)\)\s+#(\d+)\s*\n├\s*([1-9A-HJ-NP-Za-km-z]{32,44})\n└\s*#SOL\s*\(Raydium\)\s*\|\s*([\d.]+)h\s*\|\s*([\d.]+)K\s*Token Stats\n\s*├\s*USD:\s*\$([\d.₄]+)\s*\(([-+]?[\d.]+)%\)\n\s*├\s*MC:\s*\$([\d.KM]+)\n\s*├\s*Vol:\s*\$([\d.KM]+)\n\s*├\s*LP:\s*\$([\d.KM]+)\n\s*├\s*Sup:\s*([\dB/]+)\n\s*├\s*1H:\s*([-+]?[\d.]+)%\s*🅑\s*(\d+)\s*Ⓢ\s*(\d+)\n\s*└\s*ATH:\s*\$([\d.KM]+)\s*\(([-+]?[\d.]+)%\s*/\s*(\d+)m\)\s*Security\n\s*├\s*Freshies:\s*([\d.]+)%\s*1D\s*\|\s*([\d.]+)%\s*7D\n\s*├\s*Top 10:\s*([\d.]+)%\s*\|\s*(\d+)\s*\(total\)\n\s*├\s*TH:\s*([\d.\s|]+)\n\s*├\s*Dev Sold:\s*(🟢|🔴)\s*\[\]\n\s*└\s*Dex Paid:\s*(🟢|🔴)'
            match = re.search(pattern, msg_text)
            if match:
                token_name, ticker, rank, contract, age, views, usd, usd_change, mc, vol, lp, sup, change_1h, buyers, sellers, ath, ath_change, ath_time, freshies_1d, freshies_7d, top10_pct, top10_holders, th, dev_sold, dex_paid = match.groups()
                dev_sold = "Yes" if dev_sold == "🟢" else "No"
                dex_paid = "Yes" if dex_paid == "🟢" else "No"
                formatted_response = (
                    f"{token_name} (${ticker}) #{rank}\n"
                    f"├ {contract}\n"
                    f"└ #SOL (Raydium) | {age}h | {views}K Token Stats\n"
                    f" ├ USD:  ${usd} ({usd_change}%)\n"
                    f" ├ MC:   ${mc}\n"
                    f" ├ Vol:  ${vol}\n"
                    f" ├ LP:   ${lp}\n"
                    f" ├ Sup:  {sup}\n"
                    f" ├ 1H:   {change_1h}% 🅑 {buyers} Ⓢ {sellers}\n"
                    f" └ ATH:  ${ath} ({ath_change}% / {ath_time}m) Security\n"
                    f" ├ Freshies: {freshies_1d}% 1D | {freshies_7d}% 7D\n"
                    f" ├ Top 10:   {top10_pct}% | {top10_holders} (total)\n"
                    f" ├ TH:       {th}\n"
                    f" ├ Dev Sold: {dev_sold}\n"
                    f" └ Dex Paid: {dex_paid}"
                )
                logger.info(f"Phanes response: {formatted_response}")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{msg.date}] Phanes Response:\n{formatted_response}\n\n")
            else:
                logger.info("No matching Phanes response format found")
    except TypeNotFoundError as e:
        logger.error(f"TypeNotFoundError processing Phanes response: {e}. Skipping.")
    except Exception as e:
        logger.error(f"Error processing Phanes response: {e}")

async def main():
    try:
        logger.info("Starting client")
        if not phone_number:
            logger.error("PHONE_NUMBER not set")
            return
        logger.info(f"Attempting login with phone: {phone_number}")
        try:
            await client.start(phone=phone_number, password=os.getenv("PASSWORD"))
        except EOFError:
            logger.error("EOF error: Cannot prompt for login code in non-interactive environment")
            return
        logger.info("Client started")
        me = await client.get_me()
        logger.info(f"Authenticated as: {me.username or me.phone}")
        
        for chat in [source_chat, target_chat]:
            entity = await resolve_chat(client, chat)
            if not entity:
                logger.error(f"Cannot proceed: Failed to access chat {chat}")
                return
        
        logger.info(f"Forwarding started: {source_chat} → {target_chat}")
        asyncio.create_task(send_log_file())
        asyncio.create_task(status_message())
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
