







/*
#include <Wire.h>
#include <Arduino.h>

#define AS5600_ADDR 0x36
#define RAW_ANGLE_HI 0x0C

// I2C Pins for ESP32
#define SDA_PIN 18
#define SCL_PIN 19

unsigned int lastAngle = 0;
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("AS5600 Rotation Monitor Started");
}

unsigned int readRawAngle() {
  Wire.beginTransmission(AS5600_ADDR);
  Wire.write(RAW_ANGLE_HI);
  Wire.endTransmission(false);
  Wire.requestFrom(AS5600_ADDR, 2);

  if (Wire.available() == 2) {
    byte high = Wire.read();
    byte low = Wire.read();
    return ((high << 8) | low) & 0x0FFF;  // 12-bit angle (0 - 4095)
  } else {
    return lastAngle; // return last known angle on error
  }
}

void loop() {
  unsigned long now = millis();
  unsigned int angle = readRawAngle();
  int diff = angle - lastAngle;

  // Handle wrap-around
  if (diff > 2048) diff -= 4096;
  if (diff < -2048) diff += 4096;

  float deltaTime = (now - lastTime) / 1000.0; // in seconds
  float degreesMoved = (diff * 360.0) / 4096.0; // convert to degrees
  float speed = degreesMoved / deltaTime; // deg/sec

  String direction = (diff > 0) ? "Clockwise" : (diff < 0) ? "Counter-Clockwise" : "Stationary";

  Serial.print("Direction: ");
  Serial.print(direction);
  Serial.print(" | Speed: ");
  Serial.print(abs(speed), 2);
  Serial.println(" deg/sec");

  lastAngle = angle;
  lastTime = now;
  delay(100); // Adjust sampling rate as needed
}*/


/*

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

const int HALL_PIN = 32;

//const char* ssid = "raspi-webgui";
//const char* password = "bikingismylife";
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 6666;
const unsigned long udpSendInterval = 500; // Interval for sending UDP packets in milliseconds
unsigned long lastUdpSendTime = 0; // Variable to store the last time UDP packet was sent

WiFiUDP udp;

using namespace std;  // Use the std namespace for ArduinoSTL

// General control settings and flags
const int debugging = 0;
const int printResult = 1;
const int directionalMode = 1;

// Control timings in ms
const int loopTime = 60; // time between value calculation and printing in average angle reading
const int iterationCount = 20; // how many angle readings to average in one loop
const int iterationPadding = 0; // time between individual value readings

// Control settings for turn direction reading
const float turnSensitivityActivation = 6; // default: 22 - for turn direction
const float turnSensitivityDeactivation = 31;

// AS5600 device specifics
const int deviceAddress = 0x36;
const int registerAddressHigh = 0x0E; // Register for high 4 bits
const int registerAddressLow = 0x0F;  // Register for low 8 bits
const int maxSensorValue = 4095;
const int maxDegrees = 360;
const int SDA_PIN = 18;
const int SCL_PIN = 19;

//reused variables
unsigned long loopStartTime;
unsigned long loopEndTime;
unsigned long executionTime;
float lastReadAngle = 0;
int directionBufferIndex = 0;
int directionBufferSize = 0;
uint64_t directionBuffer = 0;
int turnDirection = 0;
int lastTurnDirection = 0;
int nextBit = 0;
int angleTolerance = 0;


int readValues = 0;

void AddToBuffer(int val) {
  directionBuffer = (directionBuffer << 1) | (val & 1);
}

int countOnes(uint64_t n)
{
  unsigned int c; // the total bits set in n
  for (c = 0; n; n = n & (n-1))
  {
    c++;
  }
  return c;
}

void printBufferBits() {
    int i;
    // The number of bits in a uint64_t is 64
    for (i = 63; i >= 0; i--) {
        // Check the i-th bit using bitwise AND
        uint64_t bit = (directionBuffer >> i) & 1;
        Serial.print((int)bit);
    }
    Serial.println(); // Print a new line after all bits
}

void setup() {
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.begin(115200);

  WiFi.hostname("Roll_ESP");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.print("Connecting with WiFi with ssid: ");
    Serial.print(ssid);
    Serial.print(" and password: ");
    Serial.println(password);
    Serial.println(WiFi.status());
  }

  Serial.println("Connection with WiFi successful");
  udp.begin(localUdpPort);

  loopStartTime = millis();
}

void loop() {
  if (directionalMode) {
    getRotation();
  } else {
    averageAngle();
  }

  // Check if it's time to send the UDP packet
  unsigned long currentTime = millis();
  if (currentTime - lastUdpSendTime >= udpSendInterval) {
    StaticJsonDocument<500> doc;

    String jsonStr;
    doc["sensor"] = "AS5600";
    doc["sensor_value"] = turnDirection;

    serializeJson(doc, jsonStr);

    // Read UDP messages
    int packetSize = udp.parsePacket();
    if (packetSize) {
      char packetBuffer[255];
      udp.read(packetBuffer, packetSize);

      Serial.print("Received message: ");
      Serial.println(packetBuffer);
    }

    udp.beginPacket("192.168.0.101", 6666);
    udp.print(jsonStr);
    udp.endPacket();

    // Update the last send time
    lastUdpSendTime = currentTime;
  }
}

void averageAngle() {
  loopStartTime = millis();
  float angleReadings[iterationCount];

  for (int it = 0; it < iterationCount; ++it) {
    float angle = readAngle();

    // Check if readAngle encountered an error
    if (isnan(angle)) {
      Serial.print(" !Reading Error! ");
      continue;  // Skip the rest of the loop if there's an error
    }
    angleReadings[it] = angle;
    if(iterationPadding > 0)delay(iterationPadding);
  }

  int readValuesSize = sizeof(angleReadings) / sizeof(angleReadings[0]);
  // Calculate the mean angle using the array of readings
  float averagedAngle = meanAngle(angleReadings, readValuesSize);

  if(debugging){
    Serial.println("");
    Serial.print("Raw values: ");
    Serial.println(readValuesSize);
    printArray(angleReadings, readValuesSize);
  }
  if(printResult) {
    Serial.print("Angle: ");
    Serial.println(averagedAngle, 3);  // Print with 3 decimal places
  }
  loopEndTime = millis();
  executionTime = loopEndTime - loopStartTime;
  
  if(debugging) {
    Serial.print("execution time: ");
    Serial.println(executionTime);
  }
  if(executionTime <= loopTime) {
    delay((float)(loopTime - executionTime));
  } else {
    if(debugging) {
      Serial.println("Cant keep up! Execution time of " + (String)executionTime + "ms is " + (String) (executionTime - loopTime) + "ms over the budget!");
    } else {
      Serial.println(" Device Slowdown!");
    }
  }
}

float readAngle() {
  // Request the high byte from the specified register of the device
  Wire.beginTransmission(deviceAddress);
  Wire.write(registerAddressHigh);
  int transmissionStatusHigh = Wire.endTransmission();

  if (transmissionStatusHigh != 0) {
    Serial.print("Error in I2C transmission (high byte). Status: ");
    Serial.println(transmissionStatusHigh);
    return NAN;  // Skip the rest of the loop if there's an error
  }

  Wire.requestFrom(deviceAddress, 1);

  while (Wire.available() < 1);

  byte highByte = Wire.read();

  // Request the low byte from the specified register of the device
  Wire.beginTransmission(deviceAddress);
  Wire.write(registerAddressLow);
  int transmissionStatusLow = Wire.endTransmission();

  if (transmissionStatusLow != 0) {
    Serial.print("Error in I2C transmission (low byte). Status: ");
    Serial.println(transmissionStatusLow);
    return NAN;  // Skip the rest of the loop if there's an error
  }

  Wire.requestFrom(deviceAddress, 1);

  while (Wire.available() < 1);

  byte lowByte = Wire.read();

  // Combine the high and low bytes to form a 12-bit value
  int sensorValue = (highByte << 8) | lowByte;

  // Map the sensor value to degrees
  float degrees = (float(sensorValue) / maxSensorValue) * maxDegrees;

  // Check if the angle is exactly 360.0, and if so, set it to 0.0
  if (degrees == 360.0) {
    degrees = 0.0;
  }
  readValues++;
  return degrees;
}

// Calculate the mean angle from -180 to 180 degrees
double meanAngle(const float angles[], int size) {
  double x = 0.0;
  double y = 0.0;

  for (int i = 0; i < size; ++i) {
    x += cos(angles[i] * PI / 180);
    y += sin(angles[i] * PI / 180);
  }

  return (atan2(y, x) * 180 / PI) + 180;
}

void printArray(const float arr[], int size) {
  Serial.print("[");
  for (int i = 0; i < size; ++i) {
    Serial.print(arr[i], 3);  // Print each element with 3 decimal places
    if (i < size - 1) {
      Serial.print(", ");
    }
  }
  Serial.println("]");
}

void getRotation() {
  float newAngle = readAngle();
  if(newAngle > lastReadAngle + angleTolerance) {
    AddToBuffer(1);
  } else if(newAngle < lastReadAngle - angleTolerance) {
    AddToBuffer(0);
  } else {
    nextBit = (nextBit + 1) % 2; //Add 1 and 0 in equal amounts
    AddToBuffer(nextBit);
  }

  lastReadAngle = newAngle;

  int ones = countOnes(directionBuffer);
  int zeroes = 64 - ones;
  if(debugging) {
    Serial.println("Zeroes count: " + (String)zeroes + ", Ones count: " + (String)ones + ".");
  }
  int sensitivity = (lastTurnDirection == -1 || lastTurnDirection == 1) ? turnSensitivityDeactivation : turnSensitivityActivation;
  if(ones > 64 - sensitivity) turnDirection = 1;
  else if(ones <= sensitivity) turnDirection = -1;
  else turnDirection = 0;
  
  if(printResult && lastTurnDirection != turnDirection) {
    lastTurnDirection = turnDirection;
    if(turnDirection == 1) Serial.println("Turning clockwise...");
    else if(turnDirection == -1) Serial.println("Turning counter-clockwise...");
    else if(turnDirection == 0) Serial.println("Not turning...");
  }
  if(millis() - loopStartTime > 10000){
    Serial.println("Rate of "+(String)(readValues / 10)+" values per second.");
    loopStartTime = millis();
    readValues = 0;
  }
}*/

/*#include <Arduino.h>
#include <Wire.h>
#include <ArduinoJson.h>

// ---------- Forward Declarations ----------
void getRotation();
void averageAngle();
double meanAngle(const float angles[], int size);

// ---------- General Config ----------
const int printResult = 1;
const int debugging = 0;
const int directionalMode = 1;
const int loopTime = 60;
const int iterationCount = 20;
const int iterationPadding = 0;
const unsigned long outputInterval = 500; // ms

// ---------- Turn Detection ----------
const float turnSensitivityActivation = 6;
const float turnSensitivityDeactivation = 31;

// ---------- AS5600 Settings ----------
const int deviceAddress = 0x36;
const int registerAddressHigh = 0x0E;
const int registerAddressLow = 0x0F;
const int maxSensorValue = 4095;
const int maxDegrees = 360;
const int SDA_PIN = 18;
const int SCL_PIN = 19;

// ---------- Runtime Variables ----------
unsigned long loopStartTime;
unsigned long lastOutputTime = 0;
float lastReadAngle = 0;
uint64_t directionBuffer = 0;
int turnDirection = 0;
int lastTurnDirection = 0;
int nextBit = 0;
int angleTolerance = 0;
int readValues = 0;

// ---------- Setup ----------
void setup() {
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.begin(115200);
  Serial.println("Starting AS5600 test (Serial-only, no WiFi)...");
  loopStartTime = millis();
}

// ---------- Main Loop ----------
void loop() {
  if (directionalMode) {
    getRotation();
  } else {
    averageAngle();
  }

  unsigned long currentTime = millis();
  if (currentTime - lastOutputTime >= outputInterval) {
    StaticJsonDocument<200> doc;
    doc["sensor"] = "AS5600";
    doc["sensor_value"] = turnDirection;

    String output;
    serializeJson(doc, output);
    Serial.println(output);

    lastOutputTime = currentTime;
  }
}

// ---------- Helper Functions ----------
void AddToBuffer(int val) {
  directionBuffer = (directionBuffer << 1) | (val & 1);
}

int countOnes(uint64_t n) {
  unsigned int c = 0;
  while (n) {
    n &= (n - 1);
    c++;
  }
  return c;
}

float readAngle() {
  Wire.beginTransmission(deviceAddress);
  Wire.write(registerAddressHigh);
  if (Wire.endTransmission() != 0) return NAN;

  Wire.requestFrom(deviceAddress, 1);
  while (Wire.available() < 1);
  byte highByte = Wire.read();

  Wire.beginTransmission(deviceAddress);
  Wire.write(registerAddressLow);
  if (Wire.endTransmission() != 0) return NAN;

  Wire.requestFrom(deviceAddress, 1);
  while (Wire.available() < 1);
  byte lowByte = Wire.read();

  int sensorValue = (highByte << 8) | lowByte;
  float degrees = (float(sensorValue) / maxSensorValue) * maxDegrees;
  if (degrees == 360.0) degrees = 0.0;
  readValues++;
  return degrees;
}

void getRotation() {
  float newAngle = readAngle();
  if (newAngle > lastReadAngle + angleTolerance) {
    AddToBuffer(1);
  } else if (newAngle < lastReadAngle - angleTolerance) {
    AddToBuffer(0);
  } else {
    nextBit = (nextBit + 1) % 2;
    AddToBuffer(nextBit);
  }

  lastReadAngle = newAngle;

  int ones = countOnes(directionBuffer);
  int sensitivity = (lastTurnDirection == -1 || lastTurnDirection == 1)
                    ? turnSensitivityDeactivation
                    : turnSensitivityActivation;

  if (ones > 64 - sensitivity) turnDirection = 1;
  else if (ones <= sensitivity) turnDirection = -1;
  else turnDirection = 0;

  if (printResult && lastTurnDirection != turnDirection) {
    lastTurnDirection = turnDirection;
    if (turnDirection == 1) Serial.println("Turning clockwise...");
    else if (turnDirection == -1) Serial.println("Turning counter-clockwise...");
    else Serial.println("Not turning...");
  }

  if (millis() - loopStartTime > 10000) {
    Serial.println("Rate: " + String(readValues / 10) + " values/sec");
    loopStartTime = millis();
    readValues = 0;
  }
}

void averageAngle() {
  loopStartTime = millis();
  float angleReadings[iterationCount];

  for (int i = 0; i < iterationCount; ++i) {
    float angle = readAngle();
    if (isnan(angle)) continue;
    angleReadings[i] = angle;
    if (iterationPadding > 0) delay(iterationPadding);
  }

  int size = sizeof(angleReadings) / sizeof(angleReadings[0]);
  float avgAngle = meanAngle(angleReadings, size);

  if (printResult) {
    Serial.print("Angle: ");
    Serial.println(avgAngle, 3);
  }
}

double meanAngle(const float angles[], int size) {
  double x = 0.0, y = 0.0;
  for (int i = 0; i < size; ++i) {
    x += cos(angles[i] * PI / 180);
    y += sin(angles[i] * PI / 180);
  }
  return (atan2(y, x) * 180 / PI) + 180;
}*/



#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

const int HALL_PIN = 32;

//const char* ssid = "raspi-webgui";
//const char* password = "bikingismylife";
const char *ssid = "Bicycle_Simulator_Network";
const char *password = "17701266";
unsigned int localUdpPort = 6666;
const unsigned long udpSendInterval = 500; // Interval for sending UDP packets in milliseconds
unsigned long lastUdpSendTime = 0; // Variable to store the last time UDP packet was sent

WiFiUDP udp;

using namespace std;  // Use the std namespace for ArduinoSTL

// General control settings and flags
const int debugging = 0;
const int printResult = 1;
const int directionalMode = 1;

// Control timings in ms
const int loopTime = 60; // time between value calculation and printing in average angle reading
const int iterationCount = 20; // how many angle readings to average in one loop
const int iterationPadding = 0; // time between individual value readings

// Control settings for turn direction reading
const float turnSensitivityActivation = 6; // default: 22 - for turn direction
const float turnSensitivityDeactivation = 31;

// AS5600 device specifics
const int deviceAddress = 0x36;
const int registerAddressHigh = 0x0E; // Register for high 4 bits
const int registerAddressLow = 0x0F;  // Register for low 8 bits
const int maxSensorValue = 4095;
const int maxDegrees = 360;
const int SDA_PIN = 18;
const int SCL_PIN = 19;

// Reused variables
unsigned long loopStartTime;
unsigned long loopEndTime;
unsigned long executionTime;
float lastReadAngle = 0;
int directionBufferIndex = 0;
int directionBufferSize = 0;
uint64_t directionBuffer = 0;
int turnDirection = 0;
int lastTurnDirection = 0;
int nextBit = 0;
int angleTolerance = 0;
int readValues = 0;

// ==== Function declarations (prototypes) ====
void AddToBuffer(int val);
int countOnes(uint64_t n);
void printBufferBits();
void averageAngle();
void getRotation();
float readAngle();
double meanAngle(const float angles[], int size);
void printArray(const float arr[], int size);

// ==== Setup and loop ====
void setup() {
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.begin(115200);

  WiFi.hostname("Roll_ESP");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.print("Connecting with WiFi with ssid: ");
    Serial.print(ssid);
    Serial.print(" and password: ");
    Serial.println(password);
    Serial.println(WiFi.status());
  }

  Serial.println("Connection with WiFi successful");
  udp.begin(localUdpPort);

  loopStartTime = millis();
}

void loop() {
  if (directionalMode) {
    getRotation();
  } else {
    averageAngle();
  }

  // Check if it's time to send the UDP packet
  unsigned long currentTime = millis();
  if (currentTime - lastUdpSendTime >= udpSendInterval) {
    StaticJsonDocument<500> doc;

    String jsonStr;
    doc["sensor"] = "AS5600";
    doc["sensor_value"] = turnDirection;

    serializeJson(doc, jsonStr);

    // Read UDP messages
    int packetSize = udp.parsePacket();
    if (packetSize) {
      char packetBuffer[255];
      udp.read(packetBuffer, packetSize);

      Serial.print("Received message: ");
      Serial.println(packetBuffer);
    }

    udp.beginPacket("192.168.0.101", 6666);
    udp.print(jsonStr);
    udp.endPacket();

    // Update the last send time
    lastUdpSendTime = currentTime;
  }
}

// ==== Function definitions ====

void AddToBuffer(int val) {
  directionBuffer = (directionBuffer << 1) | (val & 1);
}

int countOnes(uint64_t n)
{
  unsigned int c;
  for (c = 0; n; n = n & (n-1)) {
    c++;
  }
  return c;
}

void printBufferBits() {
  for (int i = 63; i >= 0; i--) {
    uint64_t bit = (directionBuffer >> i) & 1;
    Serial.print((int)bit);
  }
  Serial.println();
}

void averageAngle() {
  loopStartTime = millis();
  float angleReadings[iterationCount];

  for (int it = 0; it < iterationCount; ++it) {
    float angle = readAngle();
    if (isnan(angle)) {
      Serial.print(" !Reading Error! ");
      continue;
    }
    angleReadings[it] = angle;
    if (iterationPadding > 0) delay(iterationPadding);
  }

  int readValuesSize = sizeof(angleReadings) / sizeof(angleReadings[0]);
  float averagedAngle = meanAngle(angleReadings, readValuesSize);

  if (debugging) {
    Serial.println("");
    Serial.print("Raw values: ");
    Serial.println(readValuesSize);
    printArray(angleReadings, readValuesSize);
  }

  if (printResult) {
    Serial.print("Angle: ");
    Serial.println(averagedAngle, 3);
  }

  loopEndTime = millis();
  executionTime = loopEndTime - loopStartTime;

  if (debugging) {
    Serial.print("execution time: ");
    Serial.println(executionTime);
  }

  if (executionTime <= loopTime) {
    delay((float)(loopTime - executionTime));
  } else {
    if (debugging) {
      Serial.println("Cant keep up! Execution time of " + (String)executionTime + "ms is " + (String)(executionTime - loopTime) + "ms over the budget!");
    } else {
      Serial.println(" Device Slowdown!");
    }
  }
}

float readAngle() {
  Wire.beginTransmission(deviceAddress);
  Wire.write(registerAddressHigh);
  int transmissionStatusHigh = Wire.endTransmission();
  if (transmissionStatusHigh != 0) {
    Serial.print("Error in I2C transmission (high byte). Status: ");
    Serial.println(transmissionStatusHigh);
    return NAN;
  }

  Wire.requestFrom(deviceAddress, 1);
  while (Wire.available() < 1);
  byte highByte = Wire.read();

  Wire.beginTransmission(deviceAddress);
  Wire.write(registerAddressLow);
  int transmissionStatusLow = Wire.endTransmission();
  if (transmissionStatusLow != 0) {
    Serial.print("Error in I2C transmission (low byte). Status: ");
    Serial.println(transmissionStatusLow);
    return NAN;
  }

  Wire.requestFrom(deviceAddress, 1);
  while (Wire.available() < 1);
  byte lowByte = Wire.read();

  int sensorValue = (highByte << 8) | lowByte;
  float degrees = (float(sensorValue) / maxSensorValue) * maxDegrees;
  if (degrees == 360.0) degrees = 0.0;

  readValues++;
  return degrees;
}

double meanAngle(const float angles[], int size) {
  double x = 0.0;
  double y = 0.0;
  for (int i = 0; i < size; ++i) {
    x += cos(angles[i] * PI / 180);
    y += sin(angles[i] * PI / 180);
  }
  return (atan2(y, x) * 180 / PI) + 180;
}

void printArray(const float arr[], int size) {
  Serial.print("[");
  for (int i = 0; i < size; ++i) {
    Serial.print(arr[i], 3);
    if (i < size - 1) Serial.print(", ");
  }
  Serial.println("]");
}

void getRotation() {
  float newAngle = readAngle();
  if (newAngle > lastReadAngle + angleTolerance) {
    AddToBuffer(1);
  } else if (newAngle < lastReadAngle - angleTolerance) {
    AddToBuffer(0);
  } else {
    nextBit = (nextBit + 1) % 2;
    AddToBuffer(nextBit);
  }

  lastReadAngle = newAngle;

  int ones = countOnes(directionBuffer);
  int zeroes = 64 - ones;

  if (debugging) {
    Serial.println("Zeroes count: " + (String)zeroes + ", Ones count: " + (String)ones + ".");
  }

  int sensitivity = (lastTurnDirection == -1 || lastTurnDirection == 1)
                      ? turnSensitivityDeactivation
                      : turnSensitivityActivation;

  if (ones > 64 - sensitivity) turnDirection = 1;
  else if (ones <= sensitivity) turnDirection = -1;
  else turnDirection = 0;

  if (printResult && lastTurnDirection != turnDirection) {
    lastTurnDirection = turnDirection;
    if (turnDirection == 1) Serial.println("Turning clockwise...");
    else if (turnDirection == -1) Serial.println("Turning counter-clockwise...");
    else if (turnDirection == 0) Serial.println("Not turning...");
  }

  if (millis() - loopStartTime > 10000) {
    Serial.println("Rate of " + (String)(readValues / 10) + " values per second.");
    loopStartTime = millis();
    readValues = 0;
  }
}
