from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import time
import random
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CPA_LINKS = ["https://is.gd/Kr055K","https://is.gd/ArWCZo"]

user_timestamps = {}
user_balances = {}
WAIT_SECONDS = 150

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    # Check for referral
    if context.args:
        try:
            referrer_id = int(context.args[0])
            if referrer_id != user_id and user_id not in referrals:
                referrals[user_id] = referrer_id
                referral_counts[referrer_id] = referral_counts.get(referrer_id, 0) + 1
                user_balances[referrer_id] = user_balances.get(referrer_id, 0) + REFERRAL_REWARD
                await update.message.reply_text(
                    f"🎉 You were referred by user {referrer_id}. They just earned {REFERRAL_REWARD} coins!"
                )
        except ValueError:
            await update.message.reply_text("❌ Invalid referral code.")

    # Generate referral link
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"

    await update.message.reply_text(
        f"Welcome, {first_name}.\n\n"
        f"Get paid for mining tasks 🎁\n"
        f"Click /earn every 2 minutes to start earning now 🤑\n\n"
        f"👥 Invite others and earn more:\nYour referral link:\n{referral_link}"
    )


async def referrals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = referral_counts.get(user_id, 0)
    await update.message.reply_text(f"👥 You have referred {count} user(s).")

async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()
    last_earn_time = user_timestamps.get(user_id, 0)

    if now - last_earn_time < WAIT_SECONDS:
        remaining = int(WAIT_SECONDS - (now - last_earn_time))
        await update.message.reply_text(f"⏳ Please wait {remaining} more seconds before earning again.")
        return

    user_timestamps[user_id] = now

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ I Clicked", callback_data=f"claim_{user_id}")]
    ])
    await update.message.reply_text(
        f"👉 Click this link and return:\n{random.choice(CPA_LINKS)}",
        reply_markup=keyboard
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    callback_data = query.data

    # Only allow claiming if it's the user's current valid claim button
    if callback_data == f"claim_{user_id}":
        # ✅ Grant reward
        user_balances[user_id] = user_balances.get(user_id, 0) + 1
        balance = user_balances[user_id]

        # Replace button with disabled version
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Already Clicked", callback_data="disabled")]
        ])

        await query.edit_message_text(
            f"🎉 You have successfully claimed your reward!\n💰 Your balance: {balance} coins",
            reply_markup=keyboard
        )

        # Invalidate button by resetting timestamp to block new /earn until time elapses
        user_timestamps[user_id] = time.time()
    else:
        await query.edit_message_text("❌ Invalid or expired claim.")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = user_balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Your balance: {balance} coins")

# Bot setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("earn", earn))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(CommandHandler("referrals", referrals_command))

app.run_polling()
