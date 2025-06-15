from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler


async def start_command(update, context):
    user_name = update.effective_user.first_name

    button1 = InlineKeyboardButton(text="🔍 Find speaker size", callback_data="pick_product")
    button2 = InlineKeyboardButton(text="Empty Function", callback_data="empty_function_1")

    inline_keyboard = [[button1, button2]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    await update.message.reply_text(
        f"Hello, {user_name}! Welcome to B2Bro Bot chat. How can I help you?",
        reply_markup=inline_markup
    )

    return ConversationHandler.END
