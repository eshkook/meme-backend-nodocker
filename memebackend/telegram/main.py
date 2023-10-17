from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

TOKEN: Final = "6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg"
BOT_USERNAME: Final = "@zbabur_bot"

# the api gateway:
# "https://xk8r88ywm0.execute-api.eu-west-1.amazonaws.com/botox_function"

# To Steup Webhook for Telegram Bot:
# f"https://api.telegram.org/bot{TOKEN}/setWebhook"

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Keep your mouth shut and fast')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('What is so hard???')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(' It is a custom command. Quiet')     

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    words_amount = len(text.split())

    if words_amount < 5:
        response = f"You wrote {words_amount} words"
        await update.message.reply_text(response)
    else:
        keyboard = [
            [InlineKeyboardButton("because I am bored", callback_data='bored')],
            [InlineKeyboardButton("because I am afraid", callback_data='afraid')],
            [InlineKeyboardButton("because I am bad", callback_data='bad')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Why do you speak too much?', reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    choice = query.data  # This will be 'bored', 'afraid', or 'bad'

    # Define the pre-defined responses
    responses = {
        'bored': "Bored? It sounds like you need some excitement in your life.",
        'afraid': "Afraid? Don't worry, I'm here to help!",
        'bad': "Bad? Oh no! Hopefully, things will turn around soon."
    }

    # Get the response based on the user's choice
    response = responses.get(choice, "Invalid choice")

    # Send the pre-defined response
    await query.message.reply_text(response)

    # Define the new message text to indicate the selected option
    selected_option_text = {
        'bored': "You selected: because I am bored",
        'afraid': "You selected: because I am afraid",
        'bad': "You selected: because I am bad"
    }
    
    new_message_text = f'Why do you speak too much?\n{selected_option_text.get(choice, "Invalid choice")}'
    
    # Edit the original message text
    await query.message.edit_text(new_message_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type  # either private or group chat
    text: str = update.message.text  # the text that the user wrote

    print(f"User {update.message.chat.id} in {message_type}: '{text}'")

    if message_type == "group":
        if BOT_USERNAME in text:  # check if you should even response, if they talked to you
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            await handle_response(update, context, new_text)  # added await here
        else:
            return
    else:
        await handle_response(update, context, text)  # added await here

# error handling
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print("starting bot")
    app = Application.builder().token(TOKEN).build()
    
    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))     

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # callback query handler for inline keyboard buttons
    app.add_handler(CallbackQueryHandler(handle_choice))

    # errors
    app.add_error_handler(error)

    # polling 
    print("polling")
    app.run_polling(poll_interval=3) # check for messages every 3 seconds

