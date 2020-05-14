from Mqtt_and_Sensors.myMqtt_codes.my_mqtt import *
import datetime
import json
import time
import socket
import requests

# broker = 'iot.eclipse.org'
# broker = request dal catalogo
# porta = request dal catalogo


if __name__ == "__main__":

    sock = socket.create_connection(("test.mosquitto.org", 1883))
    socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

    # broker = remoteAdd[0]
    # port = remoteAdd[1]
    broker = "192.168.1.254"
    port = 1883

    topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_motion").json()

    pub = MyMQTT(clientID="Motion", topic=topic, broker=broker, port=port, isSubscriber=False)
    pub.start()
    i = 0
    motion = 0
    while True:

        if i % 2 == 0:
            motion = 1
        else:
            motion = 0
        if motion:
            pub.myPublish(msg=json.dumps({"DeviceID": "house1_Kitchen_motion", "value": motion, "time": time.time()}))
        print("value of pir :  ", motion)
        time.sleep(5)
        i += 1

    # time_pub.stop()
