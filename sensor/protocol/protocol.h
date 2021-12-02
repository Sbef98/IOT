#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <string.h>
#include <stdio.h>

#define pass ;

//////////////// STATES MANAGEMENT ////////////////////////
// So this is basically the states for reading any message through our protocol
enum Reading_states{
  message_begin,
  flags_read,
  device_id_read,
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

/*
 * This is the states that our arduino communication can be set to.
 * It is quite important to make sure that just one device is initializing at a time, since
 * the serial input is shared among all of them. 
 * When a new device is created, it has its own id not set yet => It cannot understand if a
 * message is referred to himself => To tell if the incoming message is the answer to its initialization request,
 * it needs to check the initialization flag => If its set to one, its the right message => we cannot
 * start more than one initialization at a time or things would get confused!
 */
enum controller_com_state{
  idling, // when we can get an input
  initializing_device, // WHen reading input data from serial to initialize a sensors
};

///////////////////////// MESSAGE STRCTURE ////////////////////////

#define m_init_flag     0b10000000 // Sensor Initialization Message (message initialization => m_init)
#define m_no_flags_flag 0b00000000 // A normal message
#define m_debug_flag    0b01000000 // Debug message
#define m_on_actuator_flag 0b00100000

// [FF] [Flags] [Sensor ID] [Data size] [Data] [FE]
struct Message {
  unsigned char flags;
  unsigned char device_id;
  unsigned char data_size;
  void* data;
};

/*
 * I'm using defines for a metter of commodity and preventing the overhead of a whole function declaration.
 */
#define new_empty_message(buffer)  {m_no_flags_flag, 0, 0, (buffer)}
// A string debug message is useful to send any kind of string value through the serial interface
#define new_string_debug_message(buffer) {m_debug_flag, 0,(unsigned char) strlen((buffer)), (void*) (buffer)}

// These are the results possible when using the function "read_input"
#define message_done 1        // It read a full message correctly
#define message_ok 0          // It read an input but not a full message, correctly
#define message_discarded -1  // Something went wrong when reading a message

///////////////////////// DEVICE DEFINITION /////////////////////////////

/*
 * First of all the function skeleton that should be written for each sensor. 
 * param return_data_size return_data_size is the pointer to the variable in which the sizeof() of the data
 *         that the sensor is going to return should be saved. 
 * return a void pointer to the data read by the sensor    
 */
typedef void* (*data_collector) (unsigned char* return_data_size);

/*
 * This is the function tjat represents an actuator.
 * param data_received the pointer to the data read in input
 * return a value that represents the success of the actuation
 */
typedef unsigned char (*data_eater) (void* data_received);

// A device is anything (sensor, actuator, both of them) managed by the microcontroller in use
struct device {
	data_collector sensor_func; // The function for the sensors
	data_eater actuator_func;   // The function for the actuators
	device_state state;         // The state of the device right now
  unsigned char device_id;    // The Device's id
  char* datatype;             // The data type sensed/utilized by the device
};

#define Device struct device  // Just to make it look more like a class when coding eheh

// Some defines to build a device/sensor/actuator more intuitively. A device implements both a sensing and an actuating function!
#define new_device(sensor_func, actuator_func, datatype) {(sensor_func), (actuator_func), not_initialized, 0, (datatype)}
#define new_sensor(sensor_func, datatype) {(sensor_func), NULL, not_initialized, 0, (datatype)}
#define new_actuator(actuator_func, datatype) {NULL, (actuator_func), not_initialized, 0, (datatype)}


////////////////////// FUNCTIONS //////////////////////////

/*
 * I do not uncomment these extern declarations so that they are visible only in the protocol.cpp function.
 * Basically, when importing the protocol.h file anywhere else, they will be not visible from the place
 * where it is imported: it makes them private functions!
 */

extern void send_message(struct Message* m);                                            // Comment this so that it works like a private function 
//extern char read_input(struct Message* m);                                              // Comment this so that it works like a private function 
//extern void device_start_initialization(char* data_type);                               // Comment this so that it works like a private function 
//extern void device_initialization(struct Message* m, unsigned char* device_id_to_set);  // Comment this so that it works like a private function 
//extern enum controller_com_state device_run(Device* d,                                  // Comment this so that it works like a private function 
//            struct Message* in_buffer,
//            enum controller_com_state in_buffer_state,
//            char reading_input_result
//            );

// This is basically the function that makes the whole thing possible. It becomes almost a "main" on its own
extern void controller_loop(Device* devices, unsigned char n_devices);
// THis is useful for debugging!
extern void send_debug_string(char* debug_string);

#endif // !PROTOCOL_H
