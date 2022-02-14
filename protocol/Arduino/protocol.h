#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <string.h>
#include <stdio.h>

#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1568
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951
#define NOTE_C8  4186
#define NOTE_CS8 4435
#define NOTE_D8  4699
#define NOTE_DS8 4978

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
  initialization_finished,
};

///////////////////////// MESSAGE STRCTURE ////////////////////////

#define m_init_flag     0b10000000 // Sensor Initialization Message (message initialization => m_init)
#define m_no_flags_flag 0b00000000 // A normal message
#define m_debug_flag    0b01000000 // Debug message
#define m_on_actuator_flag 0b00100000 //Actuator flag

// [FF] [Flags] [Sensor ID] [Data size] [Data] [FE]
struct Message {
  unsigned char flags;
  unsigned char device_id;
  unsigned char data_size;
  char* data;
};

/*
 * I'm using defines for a metter of commodity and preventing the overhead of a whole function declaration.
 */
#define new_empty_message(buffer)  {m_no_flags_flag, 0, 0, (char*) (buffer)}
// A string debug message is useful to send any kind of string value through the serial interface
#define new_string_debug_message(buffer) {m_debug_flag, 0,(unsigned char) strlen((buffer))+1, (char*) (buffer)}

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
struct Device {
	data_collector sensor_func; // The function for the sensors
	data_eater actuator_func;   // The function for the actuators
	device_state state;         // The state of the device right now
  unsigned char device_id;    // The Device's id
  char* datatype;             // The data type sensed/utilized by the device
};

//#define Device device  // Just to make it look more like a class when coding eheh

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
