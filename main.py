import os
from telethon import TelegramClient, events
import asyncio

# === Telegram credentials from environment variables ===
api_id = int(os.getenv('TELEGRAM_API_ID', '24066461'))
api_hash = os.getenv('TELEGRAM_API_HASH', '04d2e7ce7a20d9737960e6a69b736b4a')
phone_number = os.getenv('TELEGRAM_PHONE', '+61404319634')
client = TelegramClient("bitfoot_scraper", api_id, api_hash)

@client.on(events.NewMessage(chats=["bitfootpings"]))
async def forward(event):
    try:
        msg = event.message
        text = msg.raw_text

        if not text or "🔎" not in text:
            return

        # Cut message at the first occurrence of 🔎
        trimmed = text.split("🔎")[0].strip()

        if trimmed:
            await client.send_message("BACKENDZEROPINGxc_vy", trimmed, parse_mode="Markdown")
            await client.send_message("zeropingphane", trimmed, parse_mode="Markdown")
    except Exception as e:
        pass

@client.on(events.NewMessage(chats=["zeropingphane"]))
async def forward_lb_response(event):
    # Ignore your own outgoing "/lb" command; keep only bot’s reply
    if event.out:                # True == message you sent yourself
        return
    # Forward *as-is* (not re-sending) to the target group
    await client.forward_messages("ZeroPingX", event.message)

# ── ③ background task that sends /lb once a minute ────────────────────────────
async def ping_lb_every_minute():
    while True:
        try:
            await client.send_message("zeropingphane", "/lb")
        except Exception as e:
            print("⚠️  failed to send /lb:", e)
        await asyncio.sleep(60)           # 60 s = 1 min

with client:
    client.loop.create_task(ping_lb_every_minute())
    client.run_until_disconnected()
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
