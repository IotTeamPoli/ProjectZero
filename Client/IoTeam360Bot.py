#!/usr/bin/python
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

# Basic parameters for telegram bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
job = updater.job_queue
bot = telegram.Bot(token=TOKEN)


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


def check_presence(update, context):
    # This command has no arguments. It returns all the bluetooth beacons detected in a specific house given the chat_id
    # of the user.
    house_list = requests.get(resource_server_and_port + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
    all_inside = requests.get(presence_server_and_port + "get_all_inside").json()
    try:
        for house in house_list:
            present = []
            for person in all_inside:
                if person["home"] == house:
                    present.append("name surname: "+person["name"]+" "+person["surname"]+"\ndevice: "+person["device_name"])
            if len(present) != 0:
                text = "In house " + house + " the following people are present:\n" + "\n".join(present)
            else:
                text = "No one is inside the house " + house
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            logging.info("Presence of people requested for house " + house + " from user " + update.message.from_user.username)

    except Exception as e:
        logging.info("An error occurred in check people: " + str(e))


def check_white(update, context):
    # This command has no arguments. It returns all the people that are situated in the white list for a specific house
    # given the chat_id of the user.
    house_list = requests.get(resource_server_and_port + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
    all_white = requests.get(presence_server_and_port + "print_all_whitelist").json()
    try:
        for house in house_list:
            present = []
            for person in all_white:
                if person["home"] == house:
                    present.append(person["name"]+" "+person["surname"] + " " + person["mac"])
            if len(present) != 0:
                text = "For house " + house + " the following people are in the white list:\n" + "\n".join(present)
            else:
                text = "No one is in the white list for the house " + house
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            logging.info("White list requested for house " + house + " from user " + update.message.from_user.username)

    except Exception as e:
        logging.info("An error occurred in check white: " + str(e))


def check_black(update, context):
    # This command has no arguments. It returns all the people that are situated in the black list for a specific house
    # given the chat_id of the user.
    house_list = requests.get(resource_server_and_port + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
    all_black = requests.get(presence_server_and_port + "print_all_blacklist").json()
    try:
        for house in house_list:
            present = []
            for person in all_black:
                if person["home"] == house:
                    present.append(person["name"] + " " + person["surname"] + " " + person["mac"])
            if len(present) != 0:
                text = "For house " + house + " the following people are in the black list:\n" + "\n".join(present)
            else:
                text = "No one is in the black list for the house " + house
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            logging.info("Black list requested for house " + house + " from user " + update.message.from_user.username)

    except Exception as e:
        logging.info("An error occurred in check white: " + str(e))


def add_person_white(update, context):
    # This command takes 3 arguments. It adds a person to the whitelist (people accepted and recognized in the house).
    name = context.args[0]
    surname = context.args[1]
    mac = context.args[2]
    if len(context.args) != 3:
        text = "Please, insert a name, surname and mac address near the command /add_whitelist"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        logging.info("No arguments inserted near command /add_whitelist.")
    unknowns = requests.get(presence_server_and_port+"print_all_unknown").json()  # list of unknowns
    try:
        for i in unknowns:
            if i["mac"] == mac:
                requests.put(presence_server_and_port+"rmv_this_person", data={"mac": mac})
                i["name"] = name
                i["surname"] = surname
                requests.put(presence_server_and_port+"add_to_white", data=i)
                context.bot.sendMessage(chat_id=update.effective_chat.id, text="person added to whitelist")
                logging.info("A person was added to the white list from user: " + update.message.from_user.username)
    except Exception as e:
        logging.info("An error occurred in add person white: " + str(e))


def add_person_black(update, context):
    # This command takes 3 arguments. It adds a person in the blacklist. Every time a blacklisted person is detected in
    # the house an alert is sent to the user.
    name = context.args[0]
    surname = context.args[1]
    mac = context.args[2]
    if len(context.args) != 3:
        text = "Please, insert a name, surname and mac address near the command /add_blackist"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        logging.info("No arguments inserted near command /add_blacklist.")
    unknowns = requests.get(presence_server_and_port+"print_all_unknown").json()  # list of unknowns
    try:
        for i in unknowns:
            if i["mac"] == mac:
                requests.put(presence_server_and_port+"rmv_this_person", data={"mac": mac})
                i["name"] = name
                i["surname"] = surname
                requests.put(presence_server_and_port+"add_to_black", data=i)
                context.bot.sendMessage(chat_id=update.effective_chat.id, text="person added to blacklist")
                logging.info("A person was added to the black list from user: " + update.message.from_user.username)
    except Exception as e:
        logging.info("An error occurred add person black: " + str(e))


def get_gas(update, context):
    # Returns the gas sensed in all the houses that belong to the current user.
    house_list = requests.get(resource_server_and_port + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
    # Request from the catalog for the API key to read the thingspeak channel
    for house in house_list:
        try:
            thing_params = requests.get(resource_server_and_port + "get_chr?id=" + house+"_Kitchen_gas").json()
            channel = thing_params["channel"]
            api_key = thing_params["key"]
            field = thing_params["field"]
            # Reading of the channel
            r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                             '/last.json?api_key=' + api_key)
            # Reply to the user
            text = "Current gas value in house " + house + ": %.1f" % float(r.json()["field" + field])
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        except KeyError:
            logging.info("An error occurred: " + str(KeyError))
            text = "No gas devices detected for house " + house
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
    if len(house_list) == 0:
        text = "No houses detected with a working gas sensors"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
    logging.info("Gas requested from user " + update.message.from_user.username)



def get_temperature(update, context):
    # The argument is the room id. Returns the temperature sensed in that specific room of the house.
    house_list = requests.get(resource_server_and_port + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
    if len(context.args) != 1:
        text = "Please, insert the room id near the command /temperature"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        logging.info("No arguments inserted near command /temperature.")
        return
    room = context.args[0]
    for house in house_list:
        try:
            thing_params = requests.get(resource_server_and_port + "get_chr?id=" + house+"_"+room+"_temperature").json()
            channel = thing_params["channel"]
            api_key = thing_params["key"]
            field = thing_params["field"]
            r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                             '/last.json?api_key=' + api_key)
            text = "Current temperature in room " + room + " for house " + house + ": %.1f Celsius degrees"\
                   % float(r.json()["field" + field])
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        except KeyError:
            logging.info("An error occurred: " + str(KeyError))
            text = "No temperature devices detected for room " + room + " in house " + house
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
    if len(house_list) == 0:
        text = "No houses detected with a working temperature sensors"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
    logging.info("Temperature requested from user " + update.message.from_user.username)


def get_humidity(update, context):
    # The argument is the room id. Returns the humidity sensed in that specific room of the house.
    if len(context.args) != 1:
        text = "Please, insert the room id near the command /humidity"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        logging.info("No arguments inserted near command /humidity.")
        return
    house_list = requests.get(resource_server_and_port + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
    room = context.args[0]
    for house in house_list:
        try:
            thing_params = requests.get(resource_server_and_port + "get_chr?id=" + house+"_"+room+"_humidity").json()
            channel = thing_params["channel"]
            api_key = thing_params["key"]
            field = thing_params["field"]
            r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                             '/last.json?api_key=' + api_key)
            perc = "%"
            text = ("Current humidity in room " + room + " for house " + house + ": %.1f%s") % (float(r.json()["field" + field]),
                                                                                                 perc)
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        except KeyError:
            logging.info("An error occurred: " + str(KeyError))
            text = "No humidity devices detected for room " + room + " in house " + house
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
    if len(house_list) == 0:
        text = "No houses detected with a working humidity sensors"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
    logging.info("Humidity requested from user " + update.message.from_user.username)


def set_status(update, context):
    # The arguments are the house id and the status "ON" or "OFF". If status is ON then the motion sensor has to notify
    # a possible anomalous movement detected inside the house.
    house = context.args[0]
    status = context.args[1]
    if len(context.args) != 2:
        text = "Please, insert the house_id and the status near the command /status"
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
        logging.info("No arguments inserted near command /status.")
    try:
        requests.get(resource_server_and_port + "switch_status?id=" + house + "&status=" + status)
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Status has been switched")
        logging.info("Status of house " + house + "changed from user " + update.message.from_user.username)
    except Exception as e:
        logging.info("An error occurred: " + str(e))


def callback_gas(context):
    # This is a job queue. Periodically telegram can perform actions and automatically send messages. Here, all the
    # gas values are sensed and a user is alerted if the sensed value is above a specific threshold.
    houses = requests.get(resource_server_and_port + "get_houses").json()["houses"]
    for house in houses:
        try:
            thing_params = requests.get(resource_server_and_port + "get_chr?id=" + house + "_Kitchen" + "_gas").json()
            channel = thing_params["channel"]
            api_key = thing_params["key"]
            field = thing_params["field"]
            r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                             '/last.json?api_key=' + api_key)
            value = float(r.json()["field" + field])
            if value > 300:
                text = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS GAS VALUE HAS BEEN DETECTED!!! CHECK IF YOU TURNED OFF THE" \
                       " GAS!!!"
                # Each chat is associated with a chat id that must be specified in the catalog.
                chat_id = requests.get(resource_server_and_port + "house_chat?id=" + house).json()["chatID"]
                context.bot.sendMessage(chat_id=int(chat_id), text=text)
                context.bot.sendMessage(chat_id=int(chat_id), text="Value detected: " + str(value))
                logging.info("Gas Alert sent to house " + house)
                time.sleep(0.5)  # Avoid to get banned by telegram, limit of 30 messages per second.
        except KeyError:
            logging.info("An error occurred: " + str(KeyError) + " for house " + house + " while sensing the gas.")


def callback_pir(context):
    # This is a job queue. Periodically telegram can perform actions and automatically send messages. Here, all the
    # movement values are sensed. The user is alerted if an anomalous movement is detected when he is not at home.
    houses = requests.get(resource_server_and_port + "get_houses").json()["houses"]
    for house in houses:
        rooms = requests.get(resource_server_and_port + "get_rooms?house_id=" + house).json()["rooms"]
        for room in rooms:
            try:
                thing_params = requests.get(resource_server_and_port + "get_chr?id=" + room + "_motion").json()
                channel = thing_params["channel"]
                api_key = thing_params["key"]
                field = thing_params["field"]
                r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                                 '/last.json?api_key=' + api_key)
                value = float(r.json()["field" + field])
                if value >= 0.4 and requests.get(resource_server_and_port + "get_status?id=" + room + "_motion").json()[
                        "status"] == "ON":
                    text = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS MOVEMENT HAS BEEN DETECTED!!!"
                    # Each chat is associated with a chat id that must be specified in the catalog.
                    chat_id = requests.get(resource_server_and_port + "house_chat?id=" + house).json()["chatID"]
                    context.bot.sendMessage(chat_id=int(chat_id), text=text)
                    logging.info("Movement Alert sent for house " + house)
                    time.sleep(0.5)  # Avoid to get banned by telegram, limit of 30 messages per second.
                else:
                    print "Not entered in the statement"
            except KeyError:
                logging.info("An error occurred: " + str(KeyError) + " for house " + house + " while sensing the motion.")


def callback_black(context):
    # This job queue periodically checks the blacklist to notify the user as soon as a blacklisted person is detected in
    # the house.
    blacks = requests.get(presence_server_and_port + "print_all_blacklist").json()
    try:
        for i in blacks:
            if i["present"] == "True":
                text = "WARNING\n unwanted person entered in " + i["home"] + " : " + i["name"] + " " + i["surname"]
                chat = requests.get(resource_server_and_port + "house_chat?id=" + i["home"]).json()["chatID"]
                context.bot.sendMessage(chat_id=chat, text=text)
                logging.info("Blacklist person detected in house " + i["home"] + ". An alert was sent.")
    except Exception as e:
        logging.info("An error occurred in callback black: " + str(e))


if __name__ == '__main__':
    # List of handlers:
    start_handler = CommandHandler('start', start)
    gas_handler = CommandHandler('gas', get_gas)
    temp_handler = CommandHandler("temperature", get_temperature)
    hum_handler = CommandHandler("humidity", get_humidity)
    # status_handler = CommandHandler("set_status", set_status)
    checkpeople_handler = CommandHandler("checkpeople", check_presence)
    whitelist_handler = CommandHandler("add_whitelist", add_person_white)
    blacklist_handler = CommandHandler("add_blacklist", add_person_black)
    checkwhite_handler = CommandHandler("checkwhitelist", check_white)
    checkblack_handler = CommandHandler("checkblacklist", check_black)

    # List of dispatchers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(gas_handler)
    dispatcher.add_handler(temp_handler)
    dispatcher.add_handler(hum_handler)
    # dispatcher.add_handler(status_handler)
    dispatcher.add_handler(checkpeople_handler)
    dispatcher.add_handler(whitelist_handler)
    dispatcher.add_handler(blacklist_handler)
    dispatcher.add_handler(checkwhite_handler)
    dispatcher.add_handler(checkblack_handler)
    job_gas = job.run_repeating(callback_gas, interval=60, first=60)
    job_motion = job.run_repeating(callback_pir, interval=30, first=30)
    job_presence = job.run_repeating(callback_black, interval=60*5, first=60)

    updater.start_polling()
    updater.idle()
