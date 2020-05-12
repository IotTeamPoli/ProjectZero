from Thingspeak_Dosomething_project import *
import time

service_address = "http://0.0.0.0/8080/"
resource_address = requests.get(service_address + "get_resource").json()

if __name__ == "__main__":
	test = DoSomething("IoTeamThingSpeakAdaptor", service_address)
	test.run()
	topic = requests.get(resource_address + "get_topic?id=ResourceCatalogue").json()
	test.myMqttClient.mySubscribe(topic)  # All the topic you can have through requests

	a = 0
	while True:
		#a += 1
		time.sleep(5)

	test.end()