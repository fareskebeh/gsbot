import os
import asyncio  # 👈 Added for delay before revoking
from typing import Final 
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv 
from supabase import create_client, Client 
from dotenv import dotenv_values 

env = dotenv_values(".env") 

BOT_TOKEN: Final = env['BOT_TOKEN'] 
BOT_USERNAME: Final = env["BOT_USERNAME"]
SUPABASE_URL: Final = env["SUPABASE_URL"]
SUPABASE_KEY: Final = env["SUPABASE_KEY"]
CHANNEL_ID: Final = int(env["CHANNEL_ID"])
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text(f"Welcome {update.effective_user.first_name}\n\nEnter the command /join to check verification status and send the invite link.\n\nFor more info enter the command /help or contact the admins of the community.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("Here is the list of commands to interact with our bot:\n\n /start - Start interacting with the bot\n\n /join - Start verification process and send invite link\n\n /help - Display this message\n\nFor more info contact the admins of the community.") 

async def join_user(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user = update.effective_user 
    username = user.username 
    chat_id = update.effective_chat.id 
    if not username: 
        await update.message.reply_text("❗ You need a Telegram username to use this command\n\nFor more info use the command /help or contact the admins of the community")
        return
    result = supabase.table("profiles").select("*").eq("telegram_handle", username).execute() 
    if result.data: 
        try: 
            invite = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                creates_join_request=False
            ) 
            await update.message.reply_text(f"✅ Verified!\n\nYou can access the VIP channel using this link 👇\n\n{invite.invite_link}\n\nFor more info use the command /help or contact the admins of the community") 
            
            # 🔐 Revoke the link after a short delay (e.g. 60 seconds)
            async def revoke_link():
                await asyncio.sleep(60)
                try:
                    await context.bot.revoke_chat_invite_link(
                        chat_id=CHANNEL_ID,
                        invite_link=invite.invite_link
                    )
                except Exception as e:
                    print(f"Error revoking link: {e}")

            asyncio.create_task(revoke_link())

        except Exception as e: 
            await update.message.reply_text(f"⚠ Failed to generate invite link, Try again later.\n\nFor more info use the command /help or contact the admins of the community") 
            print(f"Error:{e}")
    else: 
        await update.message.reply_text("❌ You aren't verified!\n\nYou can visit our website to learn about our paid service 👇\n\nhttps://goldstreet.vercel.app\n\nFor more info use the command /help or contact the admins of the community") 

app = ApplicationBuilder().token(BOT_TOKEN).build() 
app.add_handler(CommandHandler("start", start)) 
app.add_handler(CommandHandler("help", help)) 
app.add_handler(CommandHandler("join", join_user)) 

if __name__ == "__main__": 
    app.run_polling()
