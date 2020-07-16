from MyMQTT_Thingspeak_project import MyMQTTAdaptor
import requests
import json


class DoSomething():
    def __init__(self, clientID, service_catalog, resource_catalog):
        # create an instance of MyMQTT class
        self.clientID = clientID
        try:
            broker_ip = str(requests.get(service_catalog + "get_broker").json())
            mqtt_port = int(requests.get(service_catalog + "get_broker_port").json())
            if mqtt_port == -1:
                raise Exception("Broker port not found.")
            self.resource_catalog = resource_catalog
            self.myMqttClient = MyMQTTAdaptor(self.clientID, broker_ip, mqtt_port, self)
        except Exception as e:
            print "Error occurred in mqtt port and broker ip retrieve: " + str(e)

    def run(self):
        # if needed, perform some other actions befor starting the mqtt communication
        print("running %s" % (self.clientID))
        self.myMqttClient.start()

    def end(self):
        # if needed, perform some other actions befor ending the software
        print("ending %s" % (self.clientID))
        self.myMqttClient.stop()

    def notify(self, topic, msg):
        # manage here your received message. You can perform some error-check here
        print("received '%s' under topic '%s'" % (msg, topic))
        # The message we expect has the format: {"Device_ID": "house_room_device", "value":value}
        # message_obj = ast.literal_eval(msg.encode("utf-8"))
        message_obj = json.loads(msg)
        device_id = message_obj["DeviceID"]
        items = message_obj["DeviceID"].split("_")
        device = items[2]
        # The values that we have to insert in thingspeak are: gas, temperature, humidity and motion.
        if (device == "gas") or (device == "temperature") or (device == "humidity"):
            try:
                # From the catalog we get the information about the write api-key and the field to be updated.
                thing_params = requests.get(self.resource_catalog + "get_chw?id=" + device_id).json()
                apiwrite = str(thing_params["key"])
                field = str(thing_params["field"])
                print("Sending The received data to ThingSpeak...")
                # Writing the information on thingspeak.
                r = requests.get("https://api.thingspeak.com/update?api_key=" + apiwrite + "&field" + field +
                                 "=" + str(message_obj["value"]))
                if r.status_code == 200:
                    print("Channel updated successfully!")
                else:
                    print("Error occurred with thingspeak channel update")
            except Exception as e:
                print "Error occurred with thingspeak channel update."
