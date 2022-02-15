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
    used_data_size = 4;
    dtostrf(temp_hum_val[1], used_data_size, 1, data_buffer);
  }
  return used_data_size;
}

int humidity (char* data_buffer)
{
  // needs https://github.com/Seeed-Studio/Grove_Temperature_And_Humidity_Sensor library
  float temp_hum_val[2] = {0};
  int used_data_size = 0;
  if (!dht.readTempAndHumidity(temp_hum_val)) {
    used_data_size = 4;
    dtostrf(temp_hum_val[0], used_data_size, 1, data_buffer);
  }
  return used_data_size;
}


int light_sensor (char* data_buffer)
{
  float value = analogRead(A0);
  int used_data_size = 3;
  dtostrf(value, used_data_size, 1, data_buffer);
  return used_data_size;
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
char light_type[] = {'l', 'i', 'g', 'h', 't', 0};

Device devices[] = {
                     new_sensor(humidity, humidity_type),
                     new_sensor(temperature, temp_type),
                     new_sensor(light_sensor, light_type),
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

   // for light sensor
   pinMode(A0, INPUT);
   
   pinMode(ledPin, OUTPUT);
   delay(1000);
}

void loop() {

  controller_loop(devices, 8);
}
