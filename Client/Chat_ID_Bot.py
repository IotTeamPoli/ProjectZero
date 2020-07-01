import telegram
from telegram.ext import Updater, CommandHandler

TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = telegram.Bot(token=TOKEN)

def chat(update, context):
	try:
		update.message.reply_text("Your chat id is: " + str(update.effective_chat.id))
	except Exception as e:
		print e


if __name__ == '__main__':
	chat_handler = CommandHandler('chat', chat)
	dispatcher.add_handler(chat_handler)
	updater.start_polling()
	updater.idle()