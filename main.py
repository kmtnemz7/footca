import os
from telethon import TelegramClient, events
import asyncio
import re
import logging

# Configure logging to /tmp/log.txt
logging.basicConfig(filename='/tmp/log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Telegram credentials from environment variables
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')
password = os.getenv('TELEGRAM_PASSWORD', 'AirJordan1!')  # For 2FA, if needed

client = TelegramClient('bitfoot_scraper', api_id, api_hash)

# Function to extract and format message before 🔎
def format_message(message):
    if not message.text or '🔎' not in message.text:
        return None
    
    # Get raw text before 🔎
    raw_text = message.text.split('🔎')[0].strip()
    if not raw_text:
        return None

    # Split lines for processing
    lines = raw_text.split('\n')
    if len(lines) < 2:
        return None

    # Extract Solana address (first line after 💊)
    solana_address_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
    match = re.search(solana_address_pattern, lines[0])
    if not match:
        return None
    address = match.group(0)

    # Initialize formatted message
    formatted_lines = [f'💊 {address}']

    # Extract token name and Solscan URL from the second line (┌)
    token_line = lines[1].strip()
    token_match = re.match(r'┌(.+?)\s*\(([^)]+)\)\s*\((https://solscan\.io/token/[^)]+)\)', token_line)
    if token_match:
        token_name, symbol, solscan_url = token_match.groups()
        formatted_lines.append(f'┌[{token_name} ({symbol})]({solscan_url})')
    else:
        formatted_lines.append(token_line)  # Fallback to raw line if parsing fails

    # Process remaining lines until TH
    th_start = None
    for i, line in enumerate(lines[2:], 2):
        if line.startswith('└TH:'):
            th_start = i
            break
        formatted_lines.append(line)

    # Process TH field with multiple hyperlinks
    if th_start is not None:
        th_line = lines[th_start].strip()
        th_values = re.findall(r'(\d+\.\d+)\s*\((https://solscan\.io/account/[^)]+)\)', th_line)
        if th_values:
            th_formatted = '└TH: ' + '|'.join(f'[{value}]({url})' for value, url in th_values)
            formatted_lines.append(th_formatted)
        else:
            formatted_lines.append(th_line)  # Fallback to raw TH line

    return '\n'.join(formatted_lines)

@client.on(events.NewMessage(chats=['bitfootpings']))
async def forward(event):
    try:
        msg = event.message
        formatted_text = format_message(msg)
        if not formatted_text:
            print('⚠️ Skipped: No deep scan info or empty text.\n' + '-' * 40)
            logging.info('Skipped: No deep scan info or empty text.')
            return

        # Detect Solana address for logging/GMGNAI_bot
        solana_address_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        match = re.search(solana_address_pattern, formatted_text)
        if match:
            address = match.group(0)
            print(f'✅ Found Solana Address: {address}')
            logging.info(f'Detected Solana Address: {address}')
            # Optional: Send to GMGNAI_bot
            # await client.send_message('GMGNAI_bot', f'New Solana CA: {address}')

        # Forward the formatted message
        await client.send_message('BACKENDZEROPINGxc_vy', formatted_text, parse_mode='Markdown')
        print(f'✅ Forwarded message to BACKENDZEROPINGxc_vy:\n{formatted_text}\n' + '-' * 40)
        logging.info(f'Forwarded to BACKENDZEROPINGxc_vy: {formatted_text}')

    except Exception as e:
        print(f'❌ Error processing message: {e}')
        logging.error(f'Error processing message: {e}')

async def main():
    try:
        await client.start(phone=phone_number, password=password)
        print('📡 Scraper started: @bitfootpings → @BACKENDZEROPINGxc_vy')
        logging.info('Scraper started')
        await client.run_until_disconnected()
    except Exception as e:
        print(f'❌ Bot error: {e}')
        logging.error(f'Bot error: {e}')

if __name__ == '__main__':
    print('🚀 Starting Bitfoot Scraper...')
    asyncio.run(main())
