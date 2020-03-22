import datetime
import json
import time
import Adafruit_DHT
import paho.mqtt.client as PahoMQTT

# broker = 'iot.eclipse.org'
# broker = request dal catalogo
# porta = request dal catalogo
class MyPublisher:
    """
    default broker and port are provided
    create publisher:
    pub = MyPublisher("ID of pub", broker, port)
    pub.start()
    pub.myPublish("topic",values)
    pub.stop()
    """
    def __init__(self, clientID, broker="192.168.1.254", port=1884):
        self.clientID = clientID
        self.port = port
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self.messageBroker = broker

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

if __name__ == "__main__":
    broker = "192.168.5.35"
    porta = 1884

    DHT_TYPE = Adafruit_DHT.DHT11
    DHT_PIN = 4  # Gpio 4

    time_pub = MyPublisher("Temp_Hum_time", broker, porta)  # change MyPublisher name into temperature
    time_pub.start()
    temp_hum = MyPublisher("temp_hum", broker, porta)
    temp_hum.start()

    while True:
        dmytime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        dmytimej = json.dumps({'current time in dd-mm-yyyy hh:mm format': dmytime})
        humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature,humidity))
        else:
            print('failed reading\n')

        print("Publishing temperature and humidity")
        print("Publishing:'%s'" % dmytime)

        time_pub.myPublish('/dmytime', dmytimej)
        temp_hum.myPublish('/temp', temperature)
        temp_hum.myPublish('/hum', humidity)

        time.sleep(30)

    time_pub.stop()
    temp_hum.stop()
