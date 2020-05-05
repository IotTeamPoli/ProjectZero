from Thingspeak_Dosomething_project import *
import time


if __name__ == "__main__":
	test = DoSomething("IoTeamThingSpeakAdaptor")
	test.run()
	topic = requests.get("http://127.0.0.1:8080/get_topic?id=ResourceCatalogue").json()
	test.myMqttClient.mySubscribe(topic)  # All the topic you can have through requests

	a = 0
	while (a < 30):
		a += 1
		time.sleep(5)

	test.end()