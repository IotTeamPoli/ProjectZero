import bluetooth
import requests
import time


# read del ip
# URL = o dal catalogo service o dal config
# casa = perforza dal config_sensor.json
if __name__ == '__main__':
    uri_w = "http://localhost:8081/print_all_whitelist"
    uri_b = "http://localhost:8081/print_all_blacklist"
    uri_u = "http://localhost:8081/print_all_unknown"
    uri_add_unknown = "http://localhost:8081/add_to_unknown"
    uri_add_white = "http://localhost:8081/add_to_white"
    uri_add_black = "http://localhost:8081/add_to_black"
    rmv = "http://localhost:8081/rmv_this_person"
    param = {"home": "house1",
             "mac": "",
             "name": "",
             "surname": "",
             "device_name": "",
             "present": "",
             "last_detected": ""}
    # get from cat then
    mac_list = []
    while True:
        # scanning
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
                if i["mac"] in mac_list:
                    print("whitelisted person detected")
                    found = 1
                    requests.put(rmv, i)
                    i["present"] = "True"
                    requests.put(uri_add_white, i)
                else:
                    found = 0
                    requests.put(rmv, i)
                    i["present"] = "False"
                    requests.put(uri_add_white, i)

            response = requests.get(uri_b)
            for i in response.json():
                if i["mac"] in mac_list:
                    print("blacklisted person detected")
                    requests.put(rmv, i)
                    i["present"] = "True"
                    requests.put(uri_add_black, i)
                    found = 1
                else:
                    found = 0
                    requests.put(rmv, i)
                    i["present"] = "False"
                    requests.put(uri_add_black, i)

            response = requests.get(uri_u)
            for i in response.json():
                if i["mac"] in mac_list:
                    print("unknown person detected")
                    requests.put(rmv, i)
                    i["present"] = "True"
                    requests.put(uri_add_unknown, i)
                    found = 1
                else:
                    found = 0
                    requests.put(rmv, i)
                    i["present"] = "False"
                    requests.put(uri_add_unknown, i)
        except Exception as e:
            print('error : ', e)

        for mac, device_name in nearby_devices:
            if not found:  #TODO and not in cat
                name = "unknown"
                surname = "unknown"
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                param["name"] = name
                param["surname"] = surname
                param["mac"] = mac
                param["device_name"] = device_name
                param["present"] = "True"
                param["last_detected"] = now
                adding = requests.put(uri_add_unknown, param)
                print("new unknown detected")
                print("added to presence catalogue with status code: ", adding.status_code)

        mac_list.clear()
        time.sleep(60)  # 60 secondi
