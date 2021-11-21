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

/*
 *  I just noticed this function is not fully "state programming" compliant. Gotta fix some ifs later.
 */
unsigned char read_input(struct Message* m)
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
    iff_m_state == sensor_id_read){
      m->sensor_id = input;
      f_m_state = data_size_read;
    }
    if(f_m_state == data_size_read){
      m->data_size = input;
      f_m_state = data_reading;
      data_read = 0;
    }
    if(f_m_state == data_reading){
      m->data[data_read++] = input; // NOTICE: post-incremente -> https://www.geeksforgeeks.org/pre-increment-and-post-increment-in-c/
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

/*
 * In this case data_type is explicitly a string.
 */
void sensor_start_initialization(char* data_type)
{
  struct message m = {m_init_flag, 0, (unsigned char) strlen(data_type), data_type, 0};
  send_message(&message);
}
/*
 * Why am i making such a tiny an simple and almost useless function?
 * So that in case in the future the intialization will be modified we can just change the code here easily.
 */
void sensor_initialization(struct Message* m, unsigned char* sensor_id_to_set)
{
  sensor_id_to_set = m->sensor_id;
}

/*
 * The sensor function it's the function that will represent our average arduino attitute.
 * It's a void because each sensor will represent a loop for a different sensor.
 * The accepted parameter is a function pointer that will basically retrieve the real
 * data for the wanted sensor. It accepts a data_buffer as input (where the collected 
 * data need to be saved, for example message.data) and returns an int (which is the size of
 * the data read).
 * 
 * The second parameter is the state of the microcontroller, which is an external control
 * to ensure that the single sensor won't overlap.
 * 
 * data_type is a zero terminated char array (a frigging string)
 * 
 */
void sensor(int (*data_collector) (char* data_buffer),
            enum Arduino_Message_Buffer_states* mc_state, 
            char* data_type, 
            )
{
  // void setup():
  /*
   * All statics won't go away every time with call this function, basically like a global,
   * but the visible only at function level, more or less like a private attribute of a class.
   */
  static enum Sensor_state sensor_state = not_initialized;    
  static unsigned char sensor_id = 0;
  static char local_message_buffer[254]; // This is used both for output and input, since i won't use both at th same time
  static struct Message message_in_buffer = {0 , 0, message_buffer, 0};

  if(sensor_state == not_initialized && *mc_state == idle){
    *mc_state = initializing;
    sensor_start_initialization(data_type);
    sensor_state = initializing;
  }
  if(sensor_state == initializing && read_input(&message_in_buffer) = 1){
    *mc_state = idle;
    sensor_initialization(message_in_buffer);
    sensor_state = initialized;
  }
  if(sensor_state == initializing && read_input(&message_in_buffer) = 0){
    pass; // basically do nothing, i should write sensor_state == initializing to be standard compliant but no i won't write anything.
  }
  if(sensor_state == initializing && read_input(&message_in_buffer) = -1){
    /*
     * Basically, the intialization went not so ok. In this case, i go back to the state 
     * of not initialized and let any other sensor that needs to use the read input buffer
     * read its own stuff and its own stuff.
     */
    sensor_state = not_initialized;
    *mc_state = idle;
  }
  /*
   * If everything its ok (the mc is not busy in some activity with
   * the outside and I am initialized, then me, a sensor,
   * I do can read the stuff i need to read and go on with my boring life of sensor
   * sending stuff to the bridge.
   */
  if(sensor_state == initialized && *mc_state = idle){
    message_in_buffer.data_size = data_collector(local_message_buffer);
    message_in_buffer.data = local_message_buffer;
    // I do not need to setup the message ID because it'll be mine for sure
    message_in_buffer.flags = m_no_flags_flag;
    send_message(&message_in_buffer);    
  }
}
