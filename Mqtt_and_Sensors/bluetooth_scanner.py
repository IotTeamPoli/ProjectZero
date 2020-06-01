import bluetooth
import requests
import time
import json

FILENAME = "config_sensors.json"
with open(FILENAME, "r") as f:
    d = json.load(f)
    IP_RASP = d["servicecat_ip"]
    house_id = d["house_id"]

PRESENCE = "../Catalog/configuration.json"
with open(PRESENCE, "r") as f:
    d = json.load(f)
    CATALOG_NAME = d["catalog_list"][2]["presence_id"]


def list_search(get_uri, add_uri, rmv, mac_lists):
    present = []
    response = requests.get(get_uri)
    for j in response.json():
        present.append(j["mac"])
        if j["mac"] in mac_lists:  # detected or not
            print("whitelisted person detected")
            requests.put(rmv, j)
            j["present"] = True
            requests.put(add_uri, j)
        else:
            requests.put(rmv, j)
            j["present"] = False
            requests.put(add_uri, j)
    return present


def connection(ip, cat_name):
    ip_presence = requests.get(ip+"get_ip?id="+cat_name)
    port = requests.get(ip+"get_port?id="+cat_name)
    return ":".join([ip_presence, str(port)])


def register_unknown(address, device, add_to_unknown):
    name = "unknown"
    surname = "unknown"
    named_tuple = time.localtime()  # get structured_time
    now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
    # format
    param = {"home": house_id,
             "mac": name,
             "name": surname,
             "surname": address,
             "device_name": device,
             "present": True,
             "last_detected": now}
    adding = requests.put(add_to_unknown, param)
    print("new unknown detected")
    print("added to presence catalogue with status code: ", adding.status_code)


def main():
    from_config = connection(IP_RASP, CATALOG_NAME)

    # default methods
    uri_get_whitelist = "http://" + from_config + "print_all_whitelist"
    uri_get_blacklist = "http://" + from_config + "print_all_blacklist"
    uri_get_unknownlist = "http://" + from_config + "print_all_unknown"
    uri_add_unknown = "http://" + from_config + "add_to_unknown"
    uri_add_white = "http://" + from_config + "add_to_white"
    uri_add_black = "http://" + from_config + "add_to_black"
    rmv = "http://" + from_config + "rmv_this_person"

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
        try:
            present_a = list_search(uri_get_whitelist, uri_add_white, rmv, mac_list)
            present_b = list_search(uri_get_blacklist, uri_add_black, rmv, mac_list)
            present_c = list_search(uri_get_unknownlist, uri_add_unknown, rmv, mac_list)
            presence_macs = present_a + present_b + present_c
        except Exception as e:
            print('error : ', e)

        for mac, device_name in nearby_devices:
            if mac not in presence_macs:  # if mac is unknown
                register_unknown(mac, device_name, uri_add_unknown)

        mac_list.clear()
        time.sleep(60)


if __name__ == '__main__':
    main()
