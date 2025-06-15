from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, filters, CommandHandler, ContextTypes
import sqlite3

CHOOSING_MODEL, CHOOSE_DOOR = range(2)
AWAITING_DOOR_SELECTION = 11


def find_car(make_model_year: str):
    parts = make_model_year.strip().split()
    if len(parts) < 3:
        return None

    make = parts[0].lower()
    model = parts[1].lower()
    try:
        year = int(parts[2])
    except ValueError:
        return None

    conn = sqlite3.connect('jbl_car_speakers.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, make, model, year FROM car_speaker_sizes
        WHERE LOWER(make) = ? AND LOWER(model) = ? AND year = ?
    """, (make, model, year))
    result = cursor.fetchone()
    conn.close()
    return result


def get_door_size(car_id, door_type):
    conn = sqlite3.connect('jbl_car_speakers.db')
    cursor = conn.cursor()
    if door_type == 'front':
        cursor.execute("SELECT front_door_size FROM car_speaker_sizes WHERE id = ?", (car_id,))
    else:
        cursor.execute("SELECT rear_door_size FROM car_speaker_sizes WHERE id = ?", (car_id,))
    size = cursor.fetchone()[0]
    conn.close()
    return size

async def start_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Enter a car model (for example: Mazda 3 2008):")
    return CHOOSING_MODEL

async def handle_model_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    car = find_car(user_input)

    if not car:
        await update.message.reply_text(
            "No car with this data found.\n"
            "Please enter in the format: Make Model Year\n"
            "For example: Mazda 3 2008"
        )
        return CHOOSING_MODEL

    car_id, make, model, year = car
    context.user_data['car_id'] = car_id

    keyboard = [
        [InlineKeyboardButton("Front door", callback_data="front")],
        [InlineKeyboardButton("Rear door", callback_data="rear")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Car found: {make} {model} {year}. Select door type:",
        reply_markup=reply_markup
    )
    return AWAITING_DOOR_SELECTION



async def door_button_handler(update, context):
    query = update.callback_query
    await query.answer()

    door_type = query.data
    car_id = context.user_data.get('car_id')
    if not car_id:
        await query.edit_message_text("Error. Start again with /start")
        return ConversationHandler.END

    size = get_door_size(car_id, door_type)

    door_name = "Front Doors" if door_type == 'front' else "Rear Doors"
    text = f"{door_name}: {size}\n\nPlease select the next option:"

    if door_type == 'front':
        keyboard = [
            [InlineKeyboardButton("Rear Doors", callback_data="rear")],
            [InlineKeyboardButton("Choose different car model", callback_data="restart_model")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Front Doors", callback_data="front")],
            [InlineKeyboardButton("Choose different car model", callback_data="restart_model")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup)

    return AWAITING_DOOR_SELECTION

async def restart_model_handler(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Enter a car model (for example: Mazda 3 2008):")
    return CHOOSING_MODEL



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel.")
    return ConversationHandler.END


conv_handler_product_picker = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_product_selection, pattern="^pick_product$")],
    states={
        CHOOSING_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_model_input)],
        AWAITING_DOOR_SELECTION: [
            CallbackQueryHandler(door_button_handler, pattern="^(front|rear)$"),
            CallbackQueryHandler(restart_model_handler, pattern="^restart_model$")
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
