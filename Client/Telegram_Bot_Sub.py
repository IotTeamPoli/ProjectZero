import paho.mqtt.client as PahoMQTT
import time
import requests
import logging
import json
from BotObject import IoTBot

# Global configuration variables
config_file = 'configuration.json'
config = open(config_file,'r')
configuration = config.read()
config.close()
config = json.loads(configuration)
service_address = config['servicecat_address']
resource_id = config["cataloglist"][1]["resource_id"]
res_address = requests.get(service_address + "get_ip?id=" + resource_id).json()
resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"])
TOKEN = "773870891:AAFuzfH48yoPrd38wckJLzYuLq95OFKvvHI"
# Initialization of log files
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    filename="info.log")


class MyBotSubscriber(object):
        def __init__(self, clientID):
            self.clientID = clientID
            # create an instance of paho.mqtt.client
            self._paho_mqtt = PahoMQTT.Client(clientID, False)

            # create the bot
            self.bot = IoTBot(TOKEN)

            # register the callback
            self._paho_mqtt.on_connect = self.myOnConnect
            self._paho_mqtt.on_message = self.myOnMessageReceived

            self.topic = requests.get(resource_address + "/get_alert_topic").json()
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
            house = topic_array[2]
            if topic_array[-1] == "alert_gas":
                chat = requests.get(resource_address + "house_chat?id=" + house).json()["chatID"]
                self.bot.sendAlert(chatid=chat, msg=msg.payload)
            elif topic_array[-1] == "alert_motion":
                chat = requests.get(resource_address + "house_chat?id=" + house).json()["chatID"]
                self.bot.sendAlert(chatid=chat, msg=msg.payload)

if __name__ == "__main__":
    botSubscriber = MyBotSubscriber("BotSubscriber1")
    botSubscriber.start()

    a = 0
    while (a < 200):
        a += 1
        time.sleep(10)

    botSubscriber.stop()