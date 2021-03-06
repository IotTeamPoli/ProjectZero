// Main Code
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>


// Update these with values suitable for your network.
const char* ssid = "Home&Life SuperWiFi-DC11";  //Nome WiFi
const char* password = "UB3LG4XR777NY3BM";      //Password WiFi
const char* mqtt_server = "192.168.1.254";      // Broker Ip -> ip raspberry

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
const int numReadings = 5;
float readings[numReadings];        // the readings from the analog input
int readIndex = 0;                  // the index of the current reading
float gas_total = 0;                // the running total
float gas_average = 0;              // the average
int inputPin = A0;

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
      // ... and resubscribe
      client.subscribe("ioteam/resourcecat/house1/Kitchen/gas");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
float gas_value;    // Gas Value
String gas_value_s; // Gas Value in string format, to be sent to the broker
float gas =0;


void setup() {
  pinMode(inputPin, INPUT);
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // initialize all the readings to 0:
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
  readings[thisReading] = 0;
    }
  // Allow the hardware to sort itself out
  delay(1500);
}


// In order to make the sensor more reliable we do the moving average over 5 minutes, detect and publish every minute.
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  else {
  // subtract the last reading:
      gas_total = gas_total - readings[readIndex];
      // read from the sensor:
      readings[readIndex] = analogRead(inputPin);
      // add the reading to the total:
      gas_total = gas_total + readings[readIndex];
      // advance to the next position in the array:
      readIndex = readIndex + 1;

      // calculate the average:
      gas_average = gas_total / numReadings;

      gas_value_s = "{\"DeviceID\":\"house1_Kitchen_gas\", \"value\":" + String(gas_average) + "}";
      char attributes[100];
      gas_value_s.toCharArray(attributes, 100); // This solves some publication issues due to the message format

      client.publish("ioteam/resourcecat/house1/Kitchen/gas", attributes);
      if (readIndex >= numReadings) {
          // ...wrap around to the beginning:
          readIndex = 0;
        }
      delay(60000); // 1 min = 60000
   }
  client.loop();
  }