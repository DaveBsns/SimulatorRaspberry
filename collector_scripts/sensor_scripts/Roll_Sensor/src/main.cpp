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
}