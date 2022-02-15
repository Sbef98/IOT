#include  "protocol.h"
#include "DHT.h"

#define DHTTYPE DHT11

#define DHTPIN 2     // what pin we're connected to（DHT10 and DHT20 don't need define it）
DHT dht(DHTPIN, DHTTYPE);

int ledState = LOW;
int ledPin = 4;

int temperature (char* data_buffer)
{
  // needs https://github.com/Seeed-Studio/Grove_Temperature_And_Humidity_Sensor library
  float temp_hum_val[2] = {0};
  int used_data_size = 0;
  if (!dht.readTempAndHumidity(temp_hum_val)) {
    dtostrf(temp_hum_val[1], 4, 1, data_buffer);
    used_data_size = 4;
  }
  return used_data_size;
}

int humidity (char* data_buffer)
{
  // needs https://github.com/Seeed-Studio/Grove_Temperature_And_Humidity_Sensor library
  float temp_hum_val[2] = {0};
  int used_data_size = 0;
  if (!dht.readTempAndHumidity(temp_hum_val)) {
    dtostrf(temp_hum_val[0], 4, 1, data_buffer);
    used_data_size = 4;
  }
  return used_data_size;
}

void* sensor_2 (unsigned char* return_data_size)
{
  static unsigned long previousMillis = 0;
  static const long interval = 10000;
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    char c[] = {'h','e','l','l','o',0};
    *return_data_size = strlen("soccmel");
    return c;
  }
  *return_data_size = 0;
}

void* sensor_3 (unsigned char* return_data_size)
{
  static unsigned long previousMillis = 0;
  static const long interval = 10000;
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    char c[] = {'s','o','c','c','m','e','l',0};
    *return_data_size = strlen("soccmel");
    return c;
  }
  *return_data_size = 0;
}

void* sensor_6 (unsigned char* return_data_size)
{
  static unsigned long previousMillis = 0;
  static const long interval = 10000;
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    char c[] = {'s','o','c','c','m','e','l',0};
    *return_data_size = strlen("soccmel");
    return c;
  }
  *return_data_size = 0;
}

void* sensor_9 (unsigned char* return_data_size)
{
  static unsigned long previousMillis = 0;
  static const long interval = 10000;
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    char c[] = {'s','o','c','c','m','e','l',0};
    *return_data_size = strlen("soccmel");
    return c;
  }
  *return_data_size = 0;
}

unsigned char actuator_1 (void* data_received)
{
  //send_debug_string("hello");
  ledState = !ledState;
  digitalWrite(ledPin,ledState);
  return 0;
}

unsigned char actuator_2 (void* data_received)
{
  //send_debug_string("hello");
  ledState = !ledState;
  digitalWrite(ledPin,ledState);
  return 0;
}
//////////////////////// GLOBAL VARS //////////////////////////////
char string_type[] = {'s','t','r','i','n','g',0};
char temp_type[] = {'t', 'e', 'm', 'p', 'e', 'r', 'a', 't', 'u', 'r', 'e', 0};
char humidity_type[] = {'h', 'u', 'm', 'i', 'd', 'i', 't', 'y', 0};
//Device s1 = {(sensor_1), NULL, not_initialized, 0, (string_type)};
//Device s1 = new_sensor(sensor_1, string_type);
//Device a1 = new_actuator(actuator_1, string_type);
Device devices[] = {
                     /*new_sensor(sensor_1, string_type),
                     new_sensor(sensor_2, string_type),
                     new_sensor(sensor_3, string_type),
                     new_sensor(sensor_6, string_type),
                     new_sensor(sensor_9, string_type),*/
                     //new_sensor(sensor_9, string_type),
                     new_sensor(humidity, humidity_type),
                     new_sensor(temperature, temp_type),
                     new_actuator(actuator_1, string_type),
                     //new_actuator(actuator_2, string_type),
                     //new_actuator(actuator_1, string_type),
                     //new_sensor(sensor_3, string_type),
                     //new_device(sensor_1, actuator_1, string_type)
                   };

void setup() {
   Serial.begin(9600);
   // for temperature and humidity sensor
   Wire.begin();
   dht.begin();
   pinMode(ledPin, OUTPUT);
   delay(1000);
}

void loop() {

  controller_loop(devices, 8);
}
