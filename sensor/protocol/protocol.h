#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <string.h>

#define pass; ;

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
enum Sensor_state{
  not_initialized,
  initializing,
  initialized,
};

// This is the states that our arduino communication can be set to
enum Arduino_Message_Buffer_states{
  idling, // when we can get an input
  initializing, // WHen reading input data from serial to initialize a sensors
};

///////////////////////// MESSAGE STRCTURE ////////////////////////
//enum Flags {
#define m_init_flag 0b00000001; // Sensor Initialization Message (message initialization => m_init)
#define m_no_flags_flag = 0b00000000;
//};

// [FF] [Flags] [Sensor ID] [Data size] [Data] [FE]
struct Message {
  unsigned char flags;
  unsigned char sensor_id;
  unsigned char data_size;
  unsigned char* data;
  //unsigned char data_read;
};

#define message_done 1
#define message_ok 0
#define message_discarded -1


extern void send_message(struct Message* m);
extern unsigned char read_input(struct Message* m);
extern void sensor_start_initialization(char* data_type);
extern void sensor_initialization(struct Message* m, unsigned char* sensor_id_to_set);
extern void sensor(int (*data_collector) (char* data_buffer),
            enum Arduino_Message_Buffer_states* mc_state, 
            char* data_type, 
            );

#endif // !PROTOCOL_H
