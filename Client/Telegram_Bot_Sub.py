import paho.mqtt.client as PahoMQTT
import time
import requests
import logging
import json
import numpy as np
from PIL import Image
from BotObject import IoTBot
import os

# Global configuration variables
config_file = '../Catalog/configuration.json'
config = open(config_file,'r')
configuration = config.read()
config.close()
config = json.loads(configuration)
service_address = config['servicecat_address']
resource_id = config["catalog_list"][1]["resource_id"]
res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"
TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"

class MyBotSubscriber(object):
        def __init__(self, clientID):
            self.clientID = clientID
            # create an instance of paho.mqtt.client
            self._paho_mqtt = PahoMQTT.Client(clientID, True)

            # create the bot
            self.bot = IoTBot(TOKEN)

            # register the callback
            self._paho_mqtt.on_connect = self.myOnConnect
            self._paho_mqtt.on_message = self.myOnMessageReceived

            self.topic = requests.get(resource_address + "get_topic?id=alert").json()
            #self.messageBroker = 'iot.eclipse.org'
            self.messageBroker = requests.get(service_address + "get_broker").json()
            self.port = requests.get(service_address + "get_broker_port").json()


        def start (self):
            # start the bot
            self.bot.start()
            #manage connection to broker
            self._paho_mqtt.connect(self.messageBroker, self.port)
            self._paho_mqtt.loop_start()
            # subscribe for a topic
            self._paho_mqtt.subscribe(self.topic, 2)

        def stop (self):
            self._paho_mqtt.unsubscribe(self.topic)
            self._paho_mqtt.loop_stop()
            self._paho_mqtt.disconnect()
            self.bot.stop()

        def myOnConnect (self, paho_mqtt, userdata, flags, rc):
            print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

        def myOnMessageReceived (self, paho_mqtt , userdata, msg):
            # A new message is received
            print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")
            topic_array = msg.topic.split("/")
            house = topic_array[3]
            payload = json.loads(msg.payload) # Payload is a dictionary
            if topic_array[-1] == "alert_gas":
                chat = requests.get(resource_address + "house_chat?id=" + house).json()["chatID"]
                self.bot.sendAlert(chatid=chat, msg=payload["gas_strategy"])
            elif topic_array[-1] == "alert_motion":
                room = payload["room"]
                chat = requests.get(resource_address + "house_chat?id=" + house).json()["chatID"]
                self.bot.sendAlert(chatid=chat, msg=payload["motion_strategy"])
                photo = payload['photo']
                if photo:# photo can be the photo array or an empty string if an error occured
                    # save the picture
                    saving_path = './'+house+'/'+room
                    print(saving_path)
                    if not os.path.exists(saving_path):
                        os.makedirs(saving_path)
                    array_ = np.asarray(photo, np.uint8)
                    image = Image.fromarray(array_, 'RGB')  # PIL Image
                    image.save(saving_path + '.jpg')
                    # call the method for sending the picture
                    self.bot.sendImage(chatid=chat, path=saving_path)

                    # qui possiamo eliminare le foto, per non averle + in memoria:
                    imagesList = os.listdir("./"+house+"/")
                    if imagesList:
                        for img in imagesList:
                            os.remove("./"+house+"/"+ img)
                        msg = 'All the pics have been removed successfully.'
                    else:
                        msg = 'Nothing to delete. Directory is already empty.'
                    # print(msg)
                else:
                    pass
                    # magari un messaggio all'utente con 'error in rendering photo'


if __name__ == "__main__":
    botSubscriber = MyBotSubscriber("BotSubscriber1")
    botSubscriber.start()

    a = 0
    while (a < 200):
        a += 1
        time.sleep(10)

    botSubscriber.stop()