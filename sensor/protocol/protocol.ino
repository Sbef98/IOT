#include  "protocol.h"

void* sensor_1 (unsigned char* return_data_size)
{
  static char c[] = {'s','o','c','c','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
}
void* sensor_2 (unsigned char* return_data_size)
{
  static char c[] = {'c','i','a','0',0};
  *return_data_size = strlen("ciao");
  return c;
}
void* sensor_3 (unsigned char* return_data_size)
{
  static char c[] = {'w','o','r','r','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
}


unsigned char actuator_1 (void* data_received)
{
  static char c[] = {'A','t','t','u','a','t','o',0};
  send_debug_string(c);
  return 0;
}

//////////////////////// GLOBAL VARS //////////////////////////////
char string_type[] = {'s','t','r','i','n','g',0};
//Device s1 = {(sensor_1), NULL, not_initialized, 0, (string_type)};
//Device s1 = new_sensor(sensor_1, string_type);
//Device a1 = new_actuator(actuator_1, string_type);
Device devices[] = {
                     new_sensor(sensor_1, string_type),
                     new_sensor(sensor_2, string_type),
                     new_sensor(sensor_3, string_type)
                     //new_actuator(actuator_1, string_type),
                     //new_device(sensor_1, actuator_1, string_type)
                   };

int ledPin = 3;
void setup() {
   Serial.begin(9600);
   pinMode(ledPin, OUTPUT);
}

void loop() {
  static char c1[] = {'L','o','o','p',' ','s','t','a','r','t',0};
  static char c2[] = {'L','o','o','p',' ','s','t','o','p', 0};;
  //send_debug_string(c1);
  controller_loop(devices, 3);
  //send_debug_string(c2);
  delay(100);
}
