import os
from telethon import TelegramClient, events
import asyncio
import re
import logging

# === Configure logging to /tmp/log.txt ===
logging.basicConfig(filename='/tmp/log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a'))
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634'))
password = "AirJordan1!"  # For 2FA, if needed
client = TelegramClient("bitfoot_scraper", api_id, api_hash)

# === Function to extract Markdown text with hyperlinks ===
def get_markdown_text(message):
    """
    Extracts the message text with Markdown formatting, including hyperlinks, up to the '🔎' symbol.
    Returns None if no text or '🔎' is not found.
    """
    if not message.text:
        return None
    
    # Split at '🔎' to get the part before
    text_parts = message.text.split("🔎")
    if len(text_parts) < 2:
        return None
    
    text = text_parts[0].strip()
    if not text:
        return None
    
    # Get message entities (e.g., URLs, bold, etc.)
    entities = message.entities or []
    if not entities:
        return text  # No formatting, return plain text
    
    # Convert entities to Markdown
    markdown_text = ""
    last_offset = 0
    for entity in entities:
        start = entity.offset
        end = start + entity.length
        # Add text before the entity
        markdown_text += text[last_offset:start]
        entity_text = text[start:end]
        
        # Handle URL entities
        if entity.__class__.__name__ == "MessageEntityTextUrl":
            markdown_text += f"[{entity_text}]({entity.url})"
        else:
            markdown_text += entity_text  # Preserve non-URL entities as plain text
        
        last_offset = end
    
    # Add remaining text after the last entity
    markdown_text += text[last_offset:]
    return markdown_text

# === Event handler for bitfootpings -> BACKENDZEROPINGxc_vy ===
@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    try:
        msg = event.message
        markdown_text = get_markdown_text(msg)

        if not markdown_text:
            print("⚠️ Skipped: No deep scan info or empty text.\n" + "-" * 40)
            logging.info("Skipped: No deep scan info or empty text.")
            return

        # Detect Solana address (optional, for GMGNAI_bot integration)
        solana_address_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        match = re.search(solana_address_pattern, markdown_text)
        if match:
            address = match.group(0)
            print(f"✅ Found Solana Address: {address}")
            logging.info(f"Detected Solana Address: {address}")
            # Optional: Send to GMGNAI_bot
            # await client.send_message("GMGNAI_bot", f"New Solana CA: {address}")

        # Forward the Markdown-formatted message
        await client.send_message("BACKENDZEROPINGxc_vy", markdown_text, parse_mode="Markdown")
        print(f"✅ Forwarded message to BACKENDZEROPINGxc_vy:\n{markdown_text}\n" + "-" * 40)
        logging.info(f"Forwarded to BACKENDZEROPINGxc_vy: {markdown_text}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")
        logging.error(f"Error processing message: {e}")

# === Async main ===
async def main():
    try:
        await client.start(phone=phone_number, password=password)
        print("📡 Scraper started: @bitfootpings → @BACKENDZEROPINGxc_vy")
        logging.info("Scraper started")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Bitfoot Scraper...")
    asyncio.run(main())
