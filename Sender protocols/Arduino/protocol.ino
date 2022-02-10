#include  "protocol.h"

int ledState = LOW;
int ledPin = 4;

void* sensor_1 (unsigned char* return_data_size)
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

void* sensor_2 (unsigned char* return_data_size)
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

void* sensor_4 (unsigned char* return_data_size)
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

void* sensor_5 (unsigned char* return_data_size)
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

void* sensor_7 (unsigned char* return_data_size)
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

void* sensor_8 (unsigned char* return_data_size)
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
void* sensor_10 (unsigned char* return_data_size)
{
  static char c[] = {'c','i','a','0',0};
  *return_data_size = strlen("ciao");
  return c;
}
void* sensor_11 (unsigned char* return_data_size)
{
  static char c[] = {'w','o','r','r','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
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
//Device s1 = {(sensor_1), NULL, not_initialized, 0, (string_type)};
//Device s1 = new_sensor(sensor_1, string_type);
//Device a1 = new_actuator(actuator_1, string_type);
Device devices[] = {
                     /*new_sensor(sensor_1, string_type),
                     new_sensor(sensor_2, string_type),
                     new_sensor(sensor_3, string_type),
                     new_sensor(sensor_4, string_type),
                     new_sensor(sensor_5, string_type),
                     new_sensor(sensor_6, string_type),
                     new_sensor(sensor_7, string_type),
                     new_sensor(sensor_8, string_type),
                     new_sensor(sensor_9, string_type),*/
                     new_sensor(sensor_9, string_type),
                     new_sensor(sensor_2, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_2, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_sensor(sensor_3, string_type),
                     //new_device(sensor_1, actuator_1, string_type)
                   };

void setup() {
   Serial.begin(9600);
   pinMode(ledPin, OUTPUT);
}

void loop() {

  controller_loop(devices, 9);
}
