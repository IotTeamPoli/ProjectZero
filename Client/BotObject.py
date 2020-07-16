# -*- coding: utf-8 -*-
import json
import logging
import requests
import telegram
from telegram.ext import Updater, CommandHandler

# Global configuration variables
config_file = '../Catalog/configuration.json'
config = open(config_file,'r')
configuration = config.read()
config.close()
try:
    config = json.loads(configuration)
    service_address = config['servicecat_address']
    resource_id = config["catalog_list"][1]["resource_id"]
    res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
    resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"
    presence_id = config["catalog_list"][2]["presence_id"]
    pres_address = requests.get(service_address + "get_address?id=" + presence_id).json()
    presence_address = "http://" + pres_address["ip"] + ":" + str(pres_address["port"]) + "/"
except Exception as e:
    print "Some catalogs might not be active yet: " + str(e)


class IoTBot(object):
    def __init__(self, token):
        self.bot = telegram.Bot(token=token)
        # Basic parameters for telegram bot
        self.updater = Updater(token=token, use_context=True)
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
            
            /gas_threshold <to change the gas threshold for alerts>
            
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
            
            - Digit "/gas" to check the gas value in your kitchen.
            
            - Digit "/gas_threshold [house] [threshold]" to change your gas threshold for alerts.
            
            - Digit "/set_status [house] [<ON/OFF>]" to activate (ON) or deactivate (OFF) motion alerts for a specific house.
            
            - Digit "/add_whitelist [name] [surname] [mac address]" to add a person in the known ones.
            
            - Digit "/add_blacklist [name] [surname] [mac address]" to add a persone in the unwanted ones.
            
            This bot will also automatically send you alerts if dangerous values of gas are detected, if a suspicious movement
            is sensed or if the bluetooth beacon of an unwanted person is detected.""")

        def check_presence(update, context):
            # This command has no arguments. It returns all the bluetooth beacons detected in a specific house given the
            # chat_id of the user.
            house_list = requests.get(resource_address + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
            all_inside = requests.get(presence_address + "get_all_inside").json()
            try:
                for house in house_list:
                    present = []
                    for person in all_inside:
                        if person["home"].split("_")[0] == house and person["device_name"] != "dummy_device":
                            present.append("mac: " + person["mac"] + "\nname surname: " + person["name"] + " " + person[
                                "surname"] + "\ndevice: " + person["device_name"]+"\n")
                    if len(present) != 0:
                        text = "In house " + house + " the following devices are detected:\n" + "\n".join(present)
                    else:
                        text = "No one is inside the house " + house
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                    print "Presence of people requested for house " + house + " from user " + update.message.from_user.username
                if len(house_list) == 0:
                    text = "No houses are associated with your chat id."
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            except Exception as e:
                print "An error occurred in check people: " + str(e)

        def check_white(update, context):
            # This command has no arguments. It returns all the people that are situated in the white list for a
            # specific house given the chat_id of the user.
            house_list = requests.get(resource_address + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
            all_white = requests.get(presence_address + "print_all_whitelist").json()
            try:
                for house in house_list:
                    present = []
                    for person in all_white:
                        if person["home"].split("_")[0] == house:
                            present.append(person["name"] + " " + person["surname"] + " " + person["mac"])
                    if len(present) != 0:
                        text = "For house " + house + " the following people are in the white list:\n" + "\n".join(
                            present)
                    else:
                        text = "No one is in the white list for the house " + house
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                    print "White list requested for house " + house + " from user " + update.message.from_user.username

                if len(house_list) == 0:
                    text = "No houses are associated with your chat id."
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            except Exception as e:
                print "An error occurred in check white: " + str(e)

        def check_black(update, context):
            # This command has no arguments. It returns all the people that are situated in the black list for a
            # specific house given the chat_id of the user.
            house_list = requests.get(resource_address + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
            all_black = requests.get(presence_address + "print_all_blacklist").json()
            try:
                for house in house_list:
                    present = []
                    for person in all_black:
                        if person["home"].split("_")[0] == house:
                            present.append(person["name"] + " " + person["surname"] + " " + person["mac"])
                    if len(present) != 0:
                        text = "For house " + house + " the following people are in the black list:\n" + "\n".join(
                            present)
                    else:
                        text = "No one is in the black list for the house " + house
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                    print "Black list requested for house " + house + " from user " + update.message.from_user.username

                if len(house_list) == 0:
                    text = "No houses are associated with your chat id."
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            except Exception as e:
                print "An error occurred in check white: " + str(e)

        def add_person_white(update, context):
            # This command takes 3 arguments. It adds a person to the whitelist (people accepted and recognized in the house).
            name = context.args[0]
            surname = context.args[1]
            mac = context.args[2]
            if len(context.args) != 3:
                text = "Please, insert a name, surname and mac address near the command /add_whitelist"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "No arguments inserted near command /add_whitelist."
            else:
                unknowns = requests.get(presence_address + "get_all_records").json()  # list of unknowns
                try:
                    for i in unknowns:
                        if i["mac"] == mac:
                            requests.put(presence_address + "rmv_this_person", data={"mac": mac})
                            i["name"] = name
                            i["surname"] = surname
                            requests.put(presence_address + "add_to_white", data=i)
                            context.bot.sendMessage(chat_id=update.effective_chat.id, text="person added to whitelist")
                            print "A person was added to the white list from user: " + update.message.from_user.username
                except Exception as e:
                    print "An error occurred in add person white: " + str(e)

        def add_person_black(update, context):
            # This command takes 3 arguments. It adds a person in the blacklist. Every time a blacklisted person is
            # detected in the house an alert is sent to the user.
            name = context.args[0]
            surname = context.args[1]
            mac = context.args[2]
            if len(context.args) != 3:
                text = "Please, insert a name, surname and mac address near the command /add_blackist"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "No arguments inserted near command /add_blacklist."
            else:
                unknowns = requests.get(presence_address + "get_all_records").json()  # list of unknowns
                try:
                    for i in unknowns:
                        if i["mac"] == mac:
                            requests.put(presence_address + "rmv_this_person", data={"mac": mac})
                            i["name"] = name
                            i["surname"] = surname
                            requests.put(presence_address + "add_to_black", data=i)
                            context.bot.sendMessage(chat_id=update.effective_chat.id, text="person added to blacklist")
                            print "A person was added to the black list from user: " + update.message.from_user.username
                except Exception as e:
                    print "An error occurred add person black: " + str(e)

        def get_gas(update, context):
            # Returns the gas sensed in all the houses that belong to the current user.
            house_list = requests.get(resource_address + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
            # Request from the catalog for the API key to read the thingspeak channel
            for house in house_list:
                try:
                    thing_params = requests.get(resource_address + "get_chr?id=" + house + "_Kitchen_gas").json()
                    channel = str(thing_params["channel"])
                    api_key = str(thing_params["key"])
                    field = str(thing_params["field"])
                    # Reading of the channel
                    r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                                     '/last.json?api_key=' + api_key)
                    # Reply to the user
                    text = "Current gas value in house " + house + ": %.1f" % float(r.json()["field" + field])
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                except KeyError:
                    print "An error occurred: " + str(KeyError)
                    text = "No gas devices detected for house " + house
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            if len(house_list) == 0:
                text = "No houses detected with a working gas sensors"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
            print "Gas requested from user " + update.message.from_user.username

        def get_temperature(update, context):
            # The argument is the room id. Returns the temperature sensed in that specific room of the house.
            house_list = requests.get(resource_address + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
            if len(context.args) != 1:
                text = "Please, insert the room id near the command /temperature"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "No arguments inserted near command /temperature."
            else:
                room = context.args[0]
                for house in house_list:
                    try:
                        thing_params = requests.get(resource_address + "get_chr?id=" + house + "_" + room + "_temperature").json()
                        channel = str(thing_params["channel"])
                        api_key = str(thing_params["key"])
                        field = str(thing_params["field"])
                        r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                                         '/last.json?api_key=' + api_key)
                        text = "Current temperature in room " + room + " for house " + house + ": %.1f Celsius degrees" \
                               % float(r.json()["field" + field])
                        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                    except KeyError:
                        print "An error occurred: " + str(KeyError)
                        text = "No temperature devices detected for room " + room + " in house " + house
                        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                if len(house_list) == 0:
                    text = "No houses detected with a working temperature sensors"
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "Temperature requested from user " + update.message.from_user.username

        def get_humidity(update, context):
            # The argument is the room id. Returns the humidity sensed in that specific room of the house.
            if len(context.args) != 1:
                text = "Please, insert the room id near the command /humidity"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "No arguments inserted near command /humidity."
            else:
                house_list = requests.get(resource_address + "chat_house?id=" + str(update.effective_chat.id)).json()["house"]
                room = context.args[0]
                for house in house_list:
                    try:
                        thing_params = requests.get(
                            resource_address + "get_chr?id=" + house + "_" + room + "_humidity").json()
                        channel = str(thing_params["channel"])
                        api_key = str(thing_params["key"])
                        field = str(thing_params["field"])
                        r = requests.get('https://api.thingspeak.com/channels/' + channel + '/fields/' + field +
                                         '/last.json?api_key=' + api_key)
                        perc = "%"
                        text = ("Current humidity in room " + room + " for house " + house + ": %.1f%s") % (
                            float(r.json()["field" + field]),
                            perc)
                        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                    except KeyError:
                        print "An error occurred: " + str(KeyError)
                        text = "No humidity devices detected for room " + room + " in house " + house
                        context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                if len(house_list) == 0:
                    text = "No houses detected with a working humidity sensors"
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "Humidity requested from user " + update.message.from_user.username

        def set_status(update, context):
            # The arguments are the house id and the status "ON" or "OFF". If status is ON then the motion sensor has to
            # notify a possible anomalous movement detected inside the house.
            house = context.args[0]
            status = context.args[1]
            if len(context.args) != 2:
                text = "Please, insert the house_id and the status near the command /status"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "No arguments inserted near command /status."
            else:
                try:
                    r = requests.get(resource_address + "switch_status?id=" + house + "&status=" + status).json()
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=r)
                    print "Status of house " + house + "changed from user " + update.message.from_user.username
                except Exception as e:
                    print "An error occurred: " + str(e)

        def change_threshold(update, context):
            if len(context.args) != 2:
                text = "Please, insert the house_id and the threshold near the command /change_gas_threshold"
                context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                print "No arguments inserted near command /change_gas_threshold."
            else:
                house = context.args[0]
                new = context.args[1]
                try:
                    r = requests.get(resource_address + "change_threshold?id=" + house + "_Kitchen_gas" + "&value=" + new).json()
                    prev_th = int(requests.get(resource_address + "get_threshold?device_id=" + house + "_Kitchen_gas").json()["threshold"])
                    if r.startswith("OK") and prev_th != -1:
                        text = "Threshold succesfully updated, from " + str(prev_th) + " to " + new
                    else:
                        text = "The threshold could not be changed for some reason."
                    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
                    print "Threshold of house " + house + "changed from user " + update.message.from_user.username
                except Exception as e:
                    print "An error occurred: " + str(e)


        def callback_black(context):
            # This job queue periodically checks the blacklist to notify the user as soon as a blacklisted person is
            # detected in the house.
            blacks = requests.get(presence_address + "print_all_blacklist").json()
            try:
                for i in blacks:
                    if i["present"]:
                        device_id = i["home"]
                        house = device_id.split("_")[0]
                        status = requests.get(resource_address + "get_status?id=" + device_id).json()
                        if status["status"] == "ON":
                            text = "WARNING\n unwanted person entered in " + house + " : " + i["name"] + " " + i[
                                "surname"]
                            chat = int(requests.get(resource_address + "house_chat?id=" + house).json()["chatID"])
                            context.bot.sendMessage(chat_id=chat, text=text)
                            print "Blacklist person detected in house " + house + ". An alert was sent."
            except Exception as e:
                print "An error occurred in callback black: " + str(e)

        start_handler = CommandHandler('start', start)
        help_handler = CommandHandler('help', help)
        gas_handler = CommandHandler('gas', get_gas)
        temp_handler = CommandHandler("temperature", get_temperature)
        hum_handler = CommandHandler("humidity", get_humidity)
        status_handler = CommandHandler("set_status", set_status)
        checkpeople_handler = CommandHandler("checkpeople", check_presence)
        whitelist_handler = CommandHandler("add_whitelist", add_person_white)
        blacklist_handler = CommandHandler("add_blacklist", add_person_black)
        checkwhite_handler = CommandHandler("checkwhitelist", check_white)
        checkblack_handler = CommandHandler("checkblacklist", check_black)
        threshold_handler = CommandHandler("gas_threshold", change_threshold)

        # List of dispatchers
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(gas_handler)
        self.dispatcher.add_handler(temp_handler)
        self.dispatcher.add_handler(hum_handler)
        self.dispatcher.add_handler(status_handler)
        self.dispatcher.add_handler(checkpeople_handler)
        self.dispatcher.add_handler(whitelist_handler)
        self.dispatcher.add_handler(blacklist_handler)
        self.dispatcher.add_handler(checkwhite_handler)
        self.dispatcher.add_handler(checkblack_handler)
        self.dispatcher.add_handler(threshold_handler)
        self.job.run_repeating(callback_black, interval=60, first=60)
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def sendAlert(self, chatid, msg):
        # In this method the alerts will be forwarded to the users
        self.bot.sendMessage(chat_id=chatid, text=msg)

    def sendImage(self, chatid, path):
        path += ".jpg"
        with open(path, 'rb') as f:
            self.bot.send_photo(chat_id=chatid, photo=f)

