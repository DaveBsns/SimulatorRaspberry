#include <Arduino.h>

#include <WiFi.h>
#include <WiFiUdp.h>

#include "BNO055_support.h"
#include <Wire.h>

#include <ArduinoJson.h>

const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 8888;

WiFiUDP udp;

struct bno055_t myBNO;
struct bno055_euler myEulerData; // Structure to hold the Euler data
struct bno055_gyro myGyroData;	 // Structure to hold the Gyro data

unsigned long lastTime = 0;

void setup()
{
	// Initialize I2C communication
	Wire.begin();

	// Create a static buffer for framing BME280 sensor data with ESP32 chip ID.

	// Initialization of the BNO055
	BNO_Init(&myBNO); // Assigning the structure to hold information about the device

	// Configuration to NDoF mode
	bno055_set_operation_mode(OPERATION_MODE_NDOF);

	delay(1);

	Serial.begin(115200);
	WiFi.hostname("Gyro_ESP");
	WiFi.begin(ssid, password);

	while (WiFi.status() != WL_CONNECTED)
	{
		delay(1000); // setting sending rate
		Serial.println("Connecting with WiFi");
	}

	Serial.println("Connection with WiFi successful");

	udp.begin(localUdpPort);
}

void loop()
{
	bno055_read_euler_hrp(&myEulerData); // Update Euler data into the structure
	StaticJsonDocument<500> doc;

	int packetSize = udp.parsePacket();

	// Method for receiving data
	if (packetSize)
	{
		char packetBuffer[255];
		udp.read(packetBuffer, packetSize);

		Serial.print("Received message: ");
		Serial.println(packetBuffer);
	}

	// Creating JSON for sensor data
	String jsonStr;
	doc["sensor"] = "BNO055";
	doc["euler_h"] = ((myEulerData.h) / 16.00);
	doc["euler_r"] = ((myEulerData.r) / 16.00);
	doc["euler_p"] = ((myEulerData.p) / 16.00);

	serializeJson(doc, jsonStr);

	udp.beginPacket("192.168.0.101", 8888);
	udp.print(jsonStr);
	udp.endPacket();

	delay(10);
}
