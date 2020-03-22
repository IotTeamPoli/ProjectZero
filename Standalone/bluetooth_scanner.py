import bluetooth
import requests
import time
import paho.mqtt.client as PahoMQTT

if __name__ == '__main__':
    while True:
        print("performing inquiry...")
        nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
        print("found %d devices" % len(nearby_devices))
        for addr, device_name in nearby_devices:
            try:
                print("\t%s - %s" % (addr, device_name))
            except Exception as e:
                print('error : ', e)
        time.sleep(5)
