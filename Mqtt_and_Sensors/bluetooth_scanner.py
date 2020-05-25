import bluetooth
import requests
import time
import json

FILENAME = "config_sensors.json"

if __name__ == '__main__':
    with open(FILENAME, "r") as f:
        d = json.load(f)
        PORT = d["service_cat_port"]
        IP_RASP = d["service_cat_ip"]
        house_id = d["house_id"]

    from_config = IP_RASP + ":" + PORT
    uri_w = "http://" + from_config + "/print_all_whitelist"
    uri_b = "http://" + from_config + "/print_all_blacklist"
    uri_u = "http://" + from_config + "/print_all_unknown"
    uri_add_unknown = "http://" + from_config + "/add_to_unknown"
    uri_add_white = "http://" + from_config + "/add_to_white"
    uri_add_black = "http://" + from_config + "/add_to_black"
    rmv = "http://" + from_config + "/rmv_this_person"
    param = {"home": house_id,
             "mac": "",
             "name": "",
             "surname": "",
             "device_name": "",
             "present": "",
             "last_detected": ""}

    mac_list = []  # detected macs
    presence_macs = []  # known macs

    while True:
        # scanning all present devices and create a list of present macs
        print("performing inquiry...")
        nearby_devices = bluetooth.discover_devices(duration=5, lookup_names=True, flush_cache=True, lookup_class=False)
        print("found %d devices" % len(nearby_devices))
        # iterating
        for mac, device_name in nearby_devices:
            try:
                mac_list.append(mac)
                print("\t%s - %s" % (mac, device_name))
            except Exception as e:
                print('error : ', e)
        found = 0
        try:
            response = requests.get(uri_w)
            for i in response.json():
                presence_macs.append(i["mac"])
                if i["mac"] in mac_list:  # detected or not
                    print("whitelisted person detected")
                    requests.put(rmv, i)
                    i["present"] = True
                    requests.put(uri_add_white, i)
                else:
                    requests.put(rmv, i)
                    i["present"] = False
                    requests.put(uri_add_white, i)

            response = requests.get(uri_b)
            for i in response.json():
                presence_macs.append(i["mac"])
                if i["mac"] in mac_list:
                    print("blacklisted person detected")
                    requests.put(rmv, i)
                    i["present"] = True
                    requests.put(uri_add_black, i)
                else:
                    requests.put(rmv, i)
                    i["present"] = False
                    requests.put(uri_add_black, i)

            response = requests.get(uri_u)
            for i in response.json():
                presence_macs.append(i["mac"])
                if i["mac"] in mac_list:
                    print("unknown person detected")
                    requests.put(rmv, i)
                    i["present"] = True
                    requests.put(uri_add_unknown, i)
                else:
                    requests.put(rmv, i)
                    i["present"] = False
                    requests.put(uri_add_unknown, i)
        except Exception as e:
            print('error : ', e)

        for mac, device_name in nearby_devices:
            if mac not in presence_macs:  # if mac is unknown
                name = "unknown"
                surname = "unknown"
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                param["name"] = name
                param["surname"] = surname
                param["mac"] = mac
                param["device_name"] = device_name
                param["present"] = True
                param["last_detected"] = now
                adding = requests.put(uri_add_unknown, param)
                print("new unknown detected")
                print("added to presence catalogue with status code: ", adding.status_code)

        mac_list.clear()
        time.sleep(60)

# TODO make better code and be more Object Oriented
