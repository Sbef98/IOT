#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <string.h>

#define pass ;

//////////////// STATES MANAGEMENT ////////////////////////
// So this is basically the states for reading any message through our protocol
enum Reading_states{
  message_begin,
  flags_read,
  sensor_id_read,
  data_size_read,
  data_reading,
  message_end
};

// This is the states that our sensors could be set to
enum device_state{
  not_initialized,
  initializing,
  initialized,
};

// This is the states that our arduino communication can be set to
enum controller_com_state{
  idling, // when we can get an input
  initializing_device, // WHen reading input data from serial to initialize a sensors
};

///////////////////////// MESSAGE STRCTURE ////////////////////////

#define m_init_flag     0b00000001 // Sensor Initialization Message (message initialization => m_init)
#define m_no_flags_flag 0b00000000
#define m_debug_flag    0b00000010
//};

// [FF] [Flags] [Sensor ID] [Data size] [Data] [FE]
struct Message {
  unsigned char flags;
  unsigned char sensor_id;
  unsigned char data_size;
  void* data;
  //unsigned char data_read;
};

#define new_empty_message(buffer)  {m_no_flags_flag, 0, 0, (buffer)}
#define new_string_debug_message(buffer) {m_debug_flag, 0,(unsigned char) strlen((buffer)), (void*) (buffer)}

#define message_done 1
#define message_ok 0
#define message_discarded -1

//////////////////////////////////////////////////////
typedef void* (*data_collector) (unsigned char* return_data_size);
typedef unsigned char (*data_eater) (void* data_received);

struct device {
	data_collector sensor_func;
	data_eater actuator_func;
	device_state state;
  unsigned char sensor_id;
  char* datatype;
};

#define Device struct device
#define new_device(sensor_func, actuator_func, datatype) {(sensor_func), (actuator_func), not_initialized, 0, (datatype)}
#define new_sensor(sensor_func, datatype) {(sensor_func), NULL, not_initialized, 0, (datatype)}
#define new_actuator(actuator_func, datatype) {NULL, (actuator_func), not_initialized, 0, (datatype)}

//extern void send_message(struct Message* m);                                            // Comment this so that it works like a private function 
//extern char read_input(struct Message* m);                                              // Comment this so that it works like a private function 
//extern void device_start_initialization(char* data_type);                               // Comment this so that it works like a private function 
//extern void device_initialization(struct Message* m, unsigned char* sensor_id_to_set);  // Comment this so that it works like a private function 
//extern enum controller_com_state device_run(Device* d,                                  // Comment this so that it works like a private function 
//            struct Message* in_buffer,
//            enum controller_com_state in_buffer_state,
//            char reading_input_result
//            );
extern void controller_loop(Device* devices, unsigned char n_devices);
extern void send_debug_string(char* debug_string);

#endif // !PROTOCOL_H
