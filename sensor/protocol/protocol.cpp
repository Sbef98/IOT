#include "protocol.h"
////////////////////// FUCTIONS TO MANAGE COMM //////////////////////
void send_message(struct Message* m)
{
  Serial.write(0xff);
  Serial.write(m->flags);
  Serial.write(m->sensor_id);
  Serial.write(m->data_size);
  for(char i = 0; i < m -> data_size; i++){
    Serial.write(((char*) m->data)[i]);
  }
  Serial.write(0xfe);
}

void send_debug_string(char* debug_string){
  struct Message m = new_string_debug_message(debug_string);
  send_message(&m);
}

void send_debug_message(struct Message* m){
  m->flags = m->flags & m_debug_flag;     //Just adding the debug flag coz so
  send_message(m);
}


/*
 *  I just noticed this function is not fully "state programming" compliant. Gotta fix some ifs later.
 */
char read_input(struct Message* m)
{
  static enum Reading_states f_m_state = message_begin;
  static unsigned char data_read = 0;
  while(Serial.available() > 0){
    
    //First of all i check if the message i'm reading already won't be broken at next read
    char input = Serial.peek(); //returns next character in buffer but does not delete it
    if(f_m_state != message_begin && input == 0xff){
      f_m_state = message_begin;
      return message_discarded;    
    }

    //Here i begin reading the actual message
    input = Serial.read();
    if(f_m_state == data_reading && input == 0xfe){
      f_m_state = message_begin;
      return message_discarded;
    }
    
    if(f_m_state == message_begin && input == 0xff)
      f_m_state = flags_read;
    
    if(f_m_state == flags_read){
      m->flags = input;
      f_m_state = sensor_id_read;
    }
    if(f_m_state == sensor_id_read){
      m->sensor_id = input;
      f_m_state = data_size_read;
    }
    if(f_m_state == data_size_read){
      m->data_size = input;
      f_m_state = data_reading;
      data_read = 0;
    }
    if(f_m_state == data_reading){
      ((char*)m->data) [data_read++] = input; // NOTICE: post-incremente -> https://www.geeksforgeeks.org/pre-increment-and-post-increment-in-c/
      if(data_read == m->data_size)
        f_m_state = message_end;
    }
    if(f_m_state == message_end && input == 0xfe){
      f_m_state = message_begin;
      if(data_read != m->data_size)
        return message_discarded;
      return message_done;
    }
  }
  return message_ok;
}

///////////////////// FUNCTION FOR DEVICES I/O //////////////////////////
void device_start_initialization(char* data_type)
{
  struct Message m = {m_init_flag, 0, (unsigned char) strlen(data_type), data_type};
  send_message(&m);
}
/*
 * Why am i making such a tiny an simple and almost useless function?
 * So that in case in the future the intialization will be modified we can just change the code here easily.
 */
void device_initialization(struct Message* m, unsigned char* sensor_id_to_set)
{
  *sensor_id_to_set = m->sensor_id;
}

////////////// MAIN LOOPS FOR DEVICES, MICROCONTROLLER ///////////////////////
enum controller_com_state device_run(Device* d,
            struct Message* in_buffer,
            enum controller_com_state in_buffer_state,
            char reading_input_result
            )
{
  if(d->state == not_initialized && in_buffer_state == idling){
    device_start_initialization(d->datatype);
    d->state = initializing;
    return initializing_device;
  }
  if(d->state == initializing && reading_input_result == message_done){
    device_initialization(in_buffer, &(d->sensor_id));
    d->state = initialized;
  }
  if(d->state == initializing && reading_input_result == message_discarded){
    d->state = not_initialized;
    return idling;
  }
  if(d->state == initialized && d->sensor_func != NULL){
    unsigned char data_size;
    void* data = d->sensor_func(&data_size);
    struct Message m = {m_no_flags_flag, d->sensor_id, data_size, data};
    send_message(&m);    
  }
  if(d->state == initialized && 
     d->actuator_func != NULL &&
     in_buffer_state == idling && 
     reading_input_result == message_done && 
     in_buffer -> flags == m_no_flags_flag &&
     in_buffer -> sensor_id == d-> sensor_id){
      d->actuator_func(in_buffer -> data);      
  }
  return idling;
}

#define buffe_size 254
void controller_loop(Device* devices, unsigned char n_devices)
{
  static char* buffer[254] = {0};
  static struct Message mc_input_buffer = new_empty_message(buffer);
  static enum controller_com_state com_state = idling;

  char read_return_result = read_input(&mc_input_buffer); // I read the input and save the result of the read
  for(unsigned char i = 0; i< n_devices; i++){
    com_state = device_run(devices + i, &mc_input_buffer, com_state, read_return_result); //devices + i it's the i-esimo pointer
  }
  
}
