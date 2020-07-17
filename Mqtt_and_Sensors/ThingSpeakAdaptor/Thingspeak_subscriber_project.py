from Thingspeak_Dosomething_project import *
import time
import json
import requests

# Global configuration variables
config_file = '../../Catalog/configuration.json'
config = open(config_file, 'r')
configuration = config.read()
config.close()
try:
    config = json.loads(configuration)
    service_address = config['servicecat_address']
    resource_id = config["catalog_list"][1]["resource_id"]
    res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
    resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"
except Exception as e:
    print "Some catalogs might not be active yet: " + str(e)

if __name__ == "__main__":
    try:
        test = DoSomething("IoTeamThingSpeakAdaptor", service_address, resource_address)
        test.run()
        topic = str(requests.get(resource_address + "get_topic?id=" + resource_id).json())
        if topic.startswith("Error"):
            raise Exception("Topic not found.")
        test.myMqttClient.mySubscribe(topic)  # All the topic you can have through requests
        while True:
            time.sleep(5)
        test.end()
    except Exception as e:
        print str(e)


