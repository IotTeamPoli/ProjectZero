import json
import requests

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
    TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"
except Exception as e:
    print ("Some catalogs might not be active yet: " + str(e))
