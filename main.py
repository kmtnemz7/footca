import os
from telethon import TelegramClient, events
import asyncio

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')
client = TelegramClient("bitfoot_scraper", api_id, api_hash)

import re
from telethon import events

def mdv2_escape(text):
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', str(text))

@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    try:
        msg = event.message
        text = msg.raw_text

        if not text:
            print("⚠️ Skipped: No text in message.")
            return
        if "🔎" not in text:
            print("⚠️ Skipped: '🔎' not in message.")
            return

        print("🟢 Parsing message...")

        trimmed = text.split("🔎")[0].strip()
        lines = trimmed.splitlines()

        token = name = usd = mc = vol = seen = dex = dex_paid = holder = th = "N/A"

        for line in lines:
            line = line.strip()
            if line.startswith("💊"):
                token = line[2:].strip()
            elif line.startswith("┌"):
                name = line[1:].strip()
            elif line.startswith("├USD:"):
                usd = line.split("USD:")[1].strip()
            elif line.startswith("├MC:"):
                mc = line.split("MC:")[1].strip()
            elif line.startswith("├Vol:"):
                vol = line.split("Vol:")[1].strip()
            elif line.startswith("├Seen:"):
                seen = line.split("Seen:")[1].strip()
            elif line.startswith("├Dex:"):
                dex = line.split("Dex:")[1].strip()
            elif line.startswith("├Dex Paid:"):
                dex_paid = line.split("Dex Paid:")[1].strip()
            elif line.startswith("├Holder:"):
                holder = line.split("Holder:")[1].strip()
            elif line.startswith("└TH:"):
                th = line.split("TH:")[1].strip()

        # Escape
        token = mdv2_escape(token)
        name = mdv2_escape(name)
        usd = mdv2_escape(usd)
        mc = mdv2_escape(mc)
        vol = mdv2_escape(vol)
        seen = mdv2_escape(seen)
        dex = mdv2_escape(dex)
        dex_paid = mdv2_escape(dex_paid)
        holder = mdv2_escape(holder)
        th = mdv2_escape(th)

        formatted = f"""💊 *{name}*
📬 CA: `{token}`

💵 *Price:* ${usd}  
📈 *Market Cap:* {mc}  
💧 *Volume:* {vol}  
⏱️ *Last Seen:* {seen} ago

⚖️ *DEX:* {dex} | 💰 Paid: `{dex_paid}`  
👥 *Holder Count:* {holder}  
🔝 *Top Holders:* {th}

*[🔼Quick trade on AXIOM\\!](https://axiom.trade/@kmtz)*"""

        print("📤 Sending message to BACKENDZEROPINGxc_vy...")
        await client.send_message("BACKENDZEROPINGxc_vy", formatted, parse_mode="MarkdownV2")

    except Exception as e:
        print("❌ Error forwarding:", e)

@client.on(events.NewMessage(chats=["bitfootpings"]))
async def detect_contract_address(event):
    try:
        text = event.message.raw_text

        if not text:
            return

        # Regex for Solana contract addresses: Base58 (32 to 44 characters)
        match = re.search(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', text)

        if match:
            contract_address = match.group(0)
            await client.send_message("zeropingphane", f"🔍 **New CA detected:**\n\n`{contract_address}`", parse_mode="MarkdownV2")

    except Exception as e:
        print("❌ CA detection error:", e)


#Filter and send back PHANES MESSAGES

#@client.on(events.NewMessage(chats="BACKENDZEROPINGxc_vy"))
#async def handle(event):
 #   msg = event.message
  #  if not msg or not msg.text:
   #     return
#
 #   full_text = msg.text
#
 #   if "DEF" in full_text:
  #      cutoff_index = full_text.find("DEF")
   #     trimmed_text = full_text[:cutoff_index].strip()
#
 #       await client.send_message(
  #          "zeropingphane",
   #         trimmed_text,
    #        parse_mode="md"  # or "MarkdownV2" if needed
     #   )
    #else:
     #   return
#
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
