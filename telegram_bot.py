from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from telegram_handlers.car_product_database_picker import conv_handler_product_picker
from telegram_handlers.start_handler import start_command
from constants import (
    TELEGRAM_BOT_TOKEN)

if TELEGRAM_BOT_TOKEN is not None:
    print("Token is correct:", TELEGRAM_BOT_TOKEN[-5:])
else:
    print("TELEGRAM_B2Bro_TOKEN is None")

extended_function = True


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))

    # Add telegram_handlers for different workflows
    application.add_handler(conv_handler_product_picker)

    application.run_polling()


if __name__ == "__main__":
    main()