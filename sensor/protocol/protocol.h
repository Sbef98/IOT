#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>
#include <SoftwareSerial.h>

//////////////// STATES MANAGEMENTE ////////////////////////
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
  initialized,
};

// This is the states that our arduino communication can be set to
enum Arduino_Message_Buffer_states{
  idling, // when we can get an input
  initializing, // WHen reading input data from serial to initialize a sensors
};

///////////////////////// MESSAGE STRCTURE ///////////////////////7
enum Flags {
  m_init = 0b00000001, // Sensor Initialization Message (message initialization => m_init)
};

// [FF] [Flags] [Sensor ID] [Data size] [Data] [FE]
struct Message {
  char flags;
  char sensor_id;
  char data_size;
  char data[256];
  char data_read;
};

extern void send_message(struct Message* m);
extern char read_input(struct Message* m, enum Reading_states* f_m_state);

#endif // !PROTOCOL_H
