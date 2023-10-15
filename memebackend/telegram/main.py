from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = "6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg"
BOT_USERNAME: Final = "@zbabur_bot"

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Keep your mouth shut and fast')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('What is so hard???')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(' It is a custom command. Quiet')     

# responses handling       
def handle_response(text: str) -> str:
    words_amount = len(text.split())
    return f"You wrote {words_amount} words"

# message handling
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type # either private or group chat
    text: str = update.message.text # the text that the user wrote

    print(f"User {update.message.chat.id} in {message_type}: '{text}'")

    if message_type == "group":
        if BOT_USERNAME in text: # check if you should even response, if they talked to you
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)  

    print('Bot', response)
    await update.message.reply_text(response)          

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

    # errors
    app.add_error_handler(error)

    # polling 
    print("polling")
    app.run_polling(poll_interval=3) # check for messages every 3 seconds

