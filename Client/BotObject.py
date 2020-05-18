# -*- coding: utf-8 -*-

import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time

# Setup parameters
# Server IP and port of the catalog
resource_server_and_port = "http://127.0.0.1:8080/"
presence_server_and_port = "http://localhost:8081/"
# Token for the telegram bot
TOKEN = "773870891:AAFuzfH48yoPrd38wckJLzYuLq95OFKvvHI"  # Check the 7
# Initialization of log files
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename="info.log")




class IoTBot(object):
    def __init__(self):
        self.bot = telegram.Bot(token=TOKEN)
        # Basic parameters for telegram bot
        self.updater = Updater(token=TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.job = self.updater.job_queue

    def start(self):
        def start(update, context):
            # Start your bot, look at the description and the commands you can use.
            update.message.reply_text('''Hello! This is IoTeam360Bot. You Can use the following commands:
            /help <how this bot works>
            /checkpeople <to check people presence in the house>
            /checkwhitelist <to check who is present in your white list>
            /checkblacklist <to check who is present in your black list>
            /temperature <to check the temperature in a specific room>
            /humidity <to check the humidity in a specific room>
            /gas <to check the gas value in a specific room>
            /add_whitelist <to add a person (name, surname, mac address) in the known ones>
            /add_blacklist <to add a person (name, surname, mac address) in the unwanted ones>
            /set_status <to activate/deactivate the alerts>
            ''')

        def help(update, context):
            update.message.reply_text("""Here how this bot works:
            - Digit "/checkpeople" to have a list of people currently detected in your house(s).
            - Digit "/checkwhitelist" to have a list of people currently present in your white list.
            - Digit "/checkblacklist" to have a list of people currently present in your black list.
            - Digit "/temperature [roomid]" to check the temperature in a specific room of your house(s).
            - Digit "/humidity [roomid]" to check the humidity in a specific room of your house(s).
            - Digit "/gas" to check the gas value in your kitchen. If the threshold is above 800 you should check it!
            - Digit "set_status [house] [<ON/OFF>]" to activate (ON) or deactivate (OFF) motion alerts for a specific house.
            - Digit "add_whitelist [name] [surname] [mac address]" to add a person in the known ones.
            - Digit "add_blacklist [name] [surname] [mac address]" to add a persone in the unwanted ones.
            This bot will also automatically send you alerts if dangerous values of gas are detected, if a suspicious movement
            is sensed when the alerts are activated or if the bluetooth beacon of an unwanted person is detected.""")

        # List of handlers:
        start_handler = CommandHandler('start', start)
        help_handler = CommandHandler('help', help)

        # List of dispatchers
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def sendAlert(self, msg):
        self.bot.sendMessage(chat_id=692640171, text=msg)

if __name__ == '__main__':
    myBot = IoTBot()
    myBot.start()
    a = 0
    while True:
        time.sleep(5)
        if a == 3:
            myBot.sendAlert("Aiutooooooooo")
        a += 1
        if a == 5:
            myBot.stop()
