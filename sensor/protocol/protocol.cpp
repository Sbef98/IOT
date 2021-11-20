#include "protocol.h"
////////////////////// FUCTIONS TO MANAGE COMM //////////////////////
void send_message(struct Message* m)
{
  Serial.write(0xff);
  Serial.write(m->flags);
  Serial.write(m->sensor_id);
  Serial.write(m->data_size);
  for(char i = 0; i < m -> data_size; i++){
    Serial.write(m->data[i]);
  }
}

// returns 0 if the read is ok
// returns -1 if the message needs to be descarded
char read_input(struct Message* m, enum Reading_states* f_m_state)
// f_m_state == future message state
{
  while(Serial.available() > 0){
    
    //First of all i check if the message i'm reading already won't be broken at next read
    char input = Serial.peek(); //returns next character in buffer but does not delete it
    if(*f_m_state != message_begin && input == 0xff){
      *f_m_state = message_begin;
      return -1;    
    }

    //Here i begin reading the actual message
    input = Serial.read();
    if(*f_m_state == data_reading && input == 0xfe){
      *f_m_state = message_begin;
      return -1;
    }
    
    if(*f_m_state == data_reading && input == 0xff)
      *f_m_state = flags_read;
    
    if(*f_m_state == flags_read){
      m->flags = input;
      *f_m_state = sensor_id_read;
    }
    if(*f_m_state == sensor_id_read){
      m->sensor_id = input;
      *f_m_state = data_size_read;
    }
    if(*f_m_state == data_size_read){
      m->data_size = input;
      *f_m_state = data_reading;
      m->data_read = 0;
    }
    if(*f_m_state == data_reading){
      m->data[m->data_read++] = input;
      if(m->data_read == m->data_size)
        *f_m_state = message_end;
    }
    if(*f_m_state == message_end && input == 0xfe){
      *f_m_state = message_begin;
      if(m->data_read != m->data_size)
        return -1;
      return 0;
    }
  }
}
