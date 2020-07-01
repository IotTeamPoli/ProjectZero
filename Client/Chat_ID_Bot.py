import telegram
from telegram.ext import Updater, CommandHandler

TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = telegram.bot(token=TOKEN)

def chat(context, update):
	print(update.effective_chad.id)

chat_handler = CommandHandler("chat", chat)
dispatcher.add_handler(chat_handler)

updater.start_polling()
updater.idle()