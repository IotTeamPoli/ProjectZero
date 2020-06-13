from Thingspeak_Dosomething_project import *
import time
import json


# Global configuration variables
config_file = '../../Catalog/configuration.json'
config = open(config_file,'r')
configuration = config.read()
config.close()
config = json.loads(configuration)
service_address = config['servicecat_address']
resource_id = config["catalog_list"][1]["resource_id"]
res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"

if __name__ == "__main__":
	test = DoSomething("IoTeamThingSpeakAdaptor", service_address)
	test.run()
	topic = requests.get(resource_address + "get_topic?id="+resource_id).json()
	test.myMqttClient.mySubscribe(topic)  # All the topic you can have through requests

	a = 0
	while True:
		#a += 1
		time.sleep(5)

	test.end()