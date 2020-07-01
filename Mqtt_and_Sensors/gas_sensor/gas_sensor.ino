/*
 Basic ESP8266 MQTT example

 This sketch demonstrates the capabilities of the pubsub library in combination
 with the ESP8266 board/library.

 It connects to an MQTT server then:
  - publishes "hello world" to the topic "ioteam/resourcecat/house1/room1/gas" every two seconds
  - subscribes to the topic "inTopic", printing out any messages
    it receives. NB - it assumes the received payloads are strings not binary
  - If the first character of the topic "inTopic" is an 1, switch ON the ESP Led,
    else switch it off

 It will reconnect to the server if the connection is lost using a blocking
 reconnect function. See the 'mqtt_reconnect_nonblocking' example for how to
 achieve the same result without blocking the main loop.

 To install the ESP8266 board, (using Arduino 1.6.4+):
  - Add the following 3rd party board manager under "File -> Preferences -> Additional Boards Manager URLs":
       http://arduino.esp8266.com/stable/package_esp8266com_index.json
  - Open the "Tools -> Board -> Board Manager" and click install for the ESP8266"
  - Select your ESP8266 in "Tools -> Board"

*/

/*
// Codice principale
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>

// Update these with values suitable for your network.

const char* ssid = "Vodafone-A41883113"; //Nome WiFi
const char* password = "84zaduv2mbycxmuf"; //Password WiFi
const char* mqtt_server = "broker.mqtt-dashboard.com"; //Ip del broker -> metti ip raspberry

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println(9600);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("ioteam/resourcecat/house1/room1/gas", "hello world");
      // ... and resubscribe
      client.subscribe("ioteam/resourcecat/house1/room1/gas");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
float gas_value; // Valore di gas
String gas_value_s; // Valore di gas formato stringa utile per mandarlo al broker
float gas =0;


void setup() {
   pinMode(A0, INPUT);
  Serial.begin(9600);

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Allow the hardware to sort itself out
  delay(1500);
}


void loop() {

  if (!client.connected()) {
    reconnect();
  }
  else {
        getsensedgas();
        delay(10000);
       }
  client.loop();
    
  }
  // Funzione principale per prelevare i valori di gas e pubblicarli sul broker
void getsensedgas()
{
  gas_value = analogRead(A0);
  gas_value_s = "{'DeviceID' : 'house1/room1/gas', 'VALUE': " + String(gas_value) + " }";
  char attributes[100];
  gas_value_s.toCharArray(attributes, 100); // Per risolvere eventuali problemi di publicazione
  client.publish("ioteam/resourcecat/house1/room1/gas", attributes);
}*/

// TODO: cambiare static topic in HTTP request
// we know ServiceCat address
// we read the resourcecat ID from configuration file
// we read conf file to know in which house the sensor is in
// now we can do topic composition

// ip raspberry (ip service cat): from configuration
// broker = requests.get(IP_Rasp + "get_broker").json()
//port_broker = requests.get(IP_Rasp + "get_broker_port").json()
//port = port_broker
//resource_ip = requests.get(IP_Rasp + "get_address?id=" + CATALOG_NAME).json()
//resource_cat = resource_ip["ip"] + ":" + str(resource_ip["port"])
//topic = requests.get("http://" + resource_cat + "/get_topic?id=" + house_id + "_" + room_id+"_motion").json()


/*
include <ESP8266HTTPClient.h>
// into the main loop (void loop of line 118) we put the http object
HTTPClient http; // declare an object of class HTTPClient
http.begin('url'); // url that we want to connect to
// then we call the get method

int httpCode = http.GET();
// if the httpCode > 0 the connection is 200. Otherwise there is an error
// if successful, we can read the response payload by caling the getString
if (httpCode > 0){
    String request_payload = http.getString();
    Serial.println(request_payload)
}
// call end at the end of the request to free the resources
http.end();
*/