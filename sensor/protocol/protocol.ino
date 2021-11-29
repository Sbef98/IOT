  #include  "protocol.h"

void* sensor_1 (unsigned char* return_data_size)
{
  static char c[] = {'s','o','c','c','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
}

unsigned char actuator_1 (void* data_received)
{
  send_debug_string("Ho Attuato!");
  return 0;
}
void* sensor_2 (unsigned char* return_data_size)
{
  static char c[] = {'s','o','c','c','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
}

unsigned char actuator_2 (void* data_received)
{
  send_debug_string("Ho Attuato!");
  return 0;
}
void* sensor_3 (unsigned char* return_data_size)
{
  static char c[] = {'s','o','c','c','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
}

unsigned char actuator_3 (void* data_received)
{
  send_debug_string("Ho Attuato!");
  return 0;
}
void* sensor_4 (unsigned char* return_data_size)
{
  static char c[] = {'s','o','c','c','m','e','l',0};
  *return_data_size = strlen("soccmel");
  return c;
}

unsigned char actuator_4 (void* data_received)
{
  send_debug_string("Ho Attuato!");
  return 0;
}
//////////////////////// GLOBAL VARS //////////////////////////////
char string_type[] = {'s','t','r','i','n','g',0};
//Device s1 = {(sensor_1), NULL, not_initialized, 0, (string_type)};
//Device s1 = new_sensor(sensor_1, string_type);
//Device a1 = new_actuator(actuator_1, string_type);
Device devices[] = { 
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_2, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_3, string_type),
                     new_sensor(sensor_2, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_2, string_type),
                     new_device(sensor_2, actuator_3, string_type),
                     new_sensor(sensor_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_2, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_3, string_type),
                     new_sensor(sensor_2, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_2, string_type),
                     new_device(sensor_2, actuator_3, string_type),
                     new_sensor(sensor_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_2, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_3, string_type),
                     new_sensor(sensor_2, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_2, string_type),
                     new_device(sensor_2, actuator_3, string_type),
                     new_sensor(sensor_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_2, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_3, string_type),
                     new_sensor(sensor_2, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_3, string_type),
                     new_actuator(actuator_2, string_type),
                     new_device(sensor_2, actuator_3, string_type),
                     new_sensor(sensor_4, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                     new_sensor(sensor_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_actuator(actuator_1, string_type),
                     new_device(sensor_1, actuator_1, string_type),
                   };

void setup() {
   
}

void loop() {
  controller_loop(devices, (unsigned char) sizeof(devices)/sizeof(Device));
}
