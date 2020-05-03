/*
 CHT IoT Client example

 It connects to an CHT IoT server by MQTT:
  - publishes publishHBPayload to publishHBTopic
  - publishes publishRawPayload to publishRawTopic
  - subscribes to subscribeLEDTopic to parse data for turn on or turn off LED
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <math.h>

// Temp sensor related constants
const int B=4275; // B value of the thermistor
const int R0 = 100000; // R0 = 100k
const int pinTempSensor = A0; // Grove - Temperature Sensor connect to A0

// Update these with values suitable for your network.

char ssid[] = "yourNetwork";     // your network SSID (name)
char pass[] = "secretPassword";  // your network password
int status  = WL_IDLE_STATUS;    // the Wifi radio's status
int heartbeat_timer = 5000;      //heatbeat timer, unit:msec
int raw_timer = 30000;         //heatbeat timer, unit:msec
char mqttServer[]     = "iot.cht.com.tw";
const char* clientId       = "amebaClient";
const char* userpass     = "yourApiKey";   //your api key
char publishHBTopic[]   = "/v1/device/yourDeviceId/heartbeat";
char publishHBPayload[] = "{\"pulse\":\"10000\"}";
char publishRawTopic[]   = "/v1/device/yourDeviceId/rawdata";
char publishRawPayload[] = "[{\"id\":\"TMP1\",\"value\":[\"99.99\"]}]";
char subscribeLEDTopic[] = "/v1/device/yourDeviceId/sensor/LED1/csv";
long previousHBTime = 0;          // previous HB previous time
long previousRawTime = 0;         // previous Raw previous time
int led_value = 0;                // led value(1:high,0:off)

WiFiClient wifiClient;
PubSubClient client(wifiClient);

//MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  char *p = (char*)payload;
  char *str;
  int element_cnt = 0;
  
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  //check LED topic or not
  if (strcmp(topic,subscribeLEDTopic) == 0){
    while ((str = strtok_r(p, ",", &p)) != NULL){ // delimiter is the semicolon
      element_cnt++;

      //check LED command is 0 or 1
      if (element_cnt == 4){
        if (str[0] == '0'){
          Serial.println("Turn off LED");
          digitalWrite(13, LOW);    // turn the LED off by making the voltage LOW
        }else if (str[0] == '1'){
          Serial.println("Turn on LED");
          digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        }
      }
    }
  }
   

}

//get temperature data
float getTemp()
{
    int a = analogRead(pinTempSensor); 
    float R = 1023.0/((float)a)-1.0;
    R = 100000.0*R;
 
    float temperature=1.0/(log(R/100000.0)/B+1/298.15)-273.15;//convert to temperature via datasheet ;
 
    Serial.print("temperature = ");
    Serial.println(temperature);

    return temperature;
}

//Send heartbeat msg task
void hbTask() {
  if(millis() - previousHBTime > heartbeat_timer){  
    previousHBTime = millis(); 
    client.publish(publishHBTopic, publishHBPayload);
    Serial.println("Publish HB Topic...");
  }
}

//Send raw msg task
void rawTask() {
  if(millis() - previousRawTime > raw_timer){  
    previousRawTime = millis(); 
    float tmp = getTemp();
    sprintf(publishRawPayload,"[{\"id\":\"TMP1\",\"value\":[\"%2.2f\"]}]",tmp);
    Serial.print("Publish Raw Payload:");
    Serial.println(publishRawPayload);
    client.publish(publishRawTopic, publishRawPayload);
  }
}



void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(clientId,userpass,userpass)) {
      Serial.println("connected");
       // ... and resubscribe
      client.subscribe(subscribeLEDTopic);
      Serial.print("Subscribe LED topic is:");
      Serial.println(subscribeLEDTopic);
      
      // Once connected, publish an announcement...
      client.publish(publishHBTopic, publishHBPayload);
      Serial.print("Public HB payload is:");
      Serial.println(publishHBPayload);
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(38400);
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }

  client.setServer(mqttServer, 1883);
  client.setCallback(callback);

  // Allow the hardware to sort itself out
  delay(1500);

  // initialize digital pin 13 as an output.
  pinMode(13, OUTPUT);
}

void loop()
{
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  //run timer task
  hbTask();
  rawTask();
}