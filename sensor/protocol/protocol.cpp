#include "protocol.h"
// checking status // 

void Message_in_started(int buzzer_pin){
    int melody[] = {
      NOTE_C4, NOTE_G3//, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4
    };
    
    // note durations: 4 = quarter note, 8 = eighth note, etc.:
    int noteDurations[] = {
      4, 8//, 8, 4, 4, 4, 4, 4
    };
    for (int thisNote = 0; thisNote < 8; thisNote++) {

    // to calculate the note duration, take one second divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(8, melody[thisNote], noteDuration);

    // to distinguish the notes, set a minimum time between them.
    // the note's duration + 30% seems to work well:
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    // stop the tone playing:
    noTone(8);
  }
}

void Message_in_finished(int buzzer_pin){
    int melody[] = {
      /*NOTE_C4, NOTE_G3,*/ NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4
    };
    
    // note durations: 4 = quarter note, 8 = eighth note, etc.:
    int noteDurations[] = {
      4, 8//, 8, 4, 4, 4, 4, 4
    };
    for (int thisNote = 0; thisNote < 8; thisNote++) {

    // to calculate the note duration, take one second divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(8, melody[thisNote], noteDuration);

    // to distinguish the notes, set a minimum time between them.
    // the note's duration + 30% seems to work well:
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    // stop the tone playing:
    noTone(8);
  }
}

void Message_in_discarded(int buzzer_pin){
    int melody[] = {
      /*NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4*/NOTE_C1,
    };
    
    // note durations: 4 = quarter note, 8 = eighth note, etc.:
    int noteDurations[] = {
      15//4, 8//, 8, 4, 4, 4, 4, 4
    };
    for (int thisNote = 0; thisNote < 8; thisNote++) {

    // to calculate the note duration, take one second divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(8, melody[thisNote], noteDuration);

    // to distinguish the notes, set a minimum time between them.
    // the note's duration + 30% seems to work well:
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    // stop the tone playing:
    noTone(8);
  }
}

////////////////////// FUCTIONS TO MANAGE COMM //////////////////////
void send_message(struct Message* m)
{
  Serial.write(0xff);
  Serial.write(m->flags);
  Serial.write(m->device_id);
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
  m->flags = m->flags | m_debug_flag;     //Just adding the debug flag coz so
  send_message(m);
}


/*
 *  I just noticed this function is not fully "state programming" compliant. Gotta fix some ifs later.
 */
char read_input(struct Message* m)
{
  ////send_debug_string("i'm in the reading input function");
  static enum Reading_states f_m_state = message_begin;
  static unsigned char data_read = 0;
  while(Serial.available() > 0){
    //send_debug_string("There is stuff in the buffer to read");
    //First of all i check if the message i'm reading already won't be broken at next read
    unsigned char input = (unsigned char) Serial.peek(); //returns next character in buffer but does not delete it
    
    if(f_m_state != message_begin && input == 0xff){
      f_m_state = message_begin;
      //send_debug_string("A new message started before the previous one finished");
      Message_in_discarded(8);
      return message_discarded;
    }

    //Here i begin reading the actual message
    input = (unsigned char) Serial.read();
    //char d[] = {(unsigned char) input, 0};
    ////send_debug_string(d);
    if(f_m_state == data_reading && input == 0xfe && data_read != m->data_size){
      f_m_state = message_begin;
      //send_debug_string("THe message finished before the reading was finished");
      return message_discarded;
    }
    
    if(f_m_state == message_begin && input == 0xff){
      f_m_state = flags_read;
      //send_debug_string("New message in input");
      continue;
    }
    
    if(f_m_state == flags_read){
      m->flags = input;
      f_m_state = device_id_read;
      //send_debug_string("Flags read");
      continue;
    }
    if(f_m_state == device_id_read){
      m->device_id = input;
      f_m_state = data_size_read;
      //send_debug_string("device_id read");
      continue;
    }
    if(f_m_state == data_size_read){
      m->data_size = input;
      f_m_state = data_reading;
      data_read = 0;
      //send_debug_string("Datasize read, starting reading input");
      continue;
    }
    if(data_read == m->data_size && f_m_state == data_reading){
        f_m_state = message_end;
        //send_debug_string("The whole message was read, let's wait for the xFE byte");
      }
    if(f_m_state == data_reading && data_read != m->data_size ){        
      ((char*)m->data) [data_read++] = input; // NOTICE: post-increment -> https://www.geeksforgeeks.org/pre-increment-and-post-increment-in-c/
      continue;
    }
    if(f_m_state == message_end && input == 0xfe){
      f_m_state = message_begin;
      if(data_read != m->data_size){
        //send_debug_string("The datasize and the data read are not maching despite we reached the 0xfe");
        //send_debug_message(m);
        return message_discarded;
      }
      //send_debug_string("Message finished! This is the message:");
      //send_debug_message(m);
      return message_done;
    }
  }
  return message_ok;
}

///////////////////// FUNCTION FOR DEVICES I/O //////////////////////////
void device_start_initialization(char* data_type, bool actuator)
{
  struct Message m = {(m_init_flag | (actuator == true ? m_on_actuator_flag : 0)), 0, (unsigned char) strlen(data_type), data_type};
  send_message(&m);
  //char flag_char[] = {(m_init_flag | (actuator == true ? m_on_actuator_flag : 0)), 0};
  ////send_debug_string(flag_char);
}
/*
 * Why am i making such a tiny an simple and almost useless function?
 * So that in case in the future the intialization will be modified we can just change the code here easily.
 */
void device_initialization(struct Message* m, unsigned char* device_id_to_set)
{
  *device_id_to_set = m->device_id;
}

////////////// MAIN LOOPS FOR DEVICES, MICROCONTROLLER ///////////////////////


//This is the function that will manage the single device state
enum controller_com_state device_run(Device* d,
            struct Message* in_buffer,
            enum controller_com_state in_buffer_state,
            char reading_input_result
            )
{  
  // Checking if device needs to be initialized and if i'm currently allowed to start initialization 
  if(d->state == not_initialized && in_buffer_state == idling && d->actuator_func != NULL){
    device_start_initialization(d->datatype, true);
    d->state = initializing;
    digitalWrite(4, HIGH);
    return initializing_device; // We tell to the microcontroller that i need to be the only one initializing rn
  }
  
  if(d->state == not_initialized && in_buffer_state == idling && d->actuator_func == NULL){
    device_start_initialization(d->datatype, false);
    d->state = initializing;
    return initializing_device; // We tell to the microcontroller that i need to be the only one initializing rn
  }
  
  // If we get in input an initialization answer it completes the initialization
  if(d->state == initializing && reading_input_result == message_done && (in_buffer -> flags & m_init_flag) != 0){
    if(d->actuator_func != NULL)
      digitalWrite(4, LOW);
    device_initialization(in_buffer, &(d->device_id));
    d->state = initialized;
    return initialization_finished;
  }
  // If the incoming message was broken, we cannot tell if the initialization went well.
  // THIS MAY BE A WEAK POINT OF OUR STRATEGY. NEEDS TO BE HANDLED SOMEHOW BETTER THAN THIS
  // ESPECIALLY ON THE BRIDGE SIDE I GUESS!
  if(d->state == initializing && reading_input_result == message_discarded){
    d->state = not_initialized;
    return idling;
  }
  // If we are an initialized sensor, let's send some fresh datas!
  if(d->state == initialized && d->sensor_func != NULL){
    unsigned char data_size;
    void* data = d->sensor_func(&data_size);
    if(data_size > 0){
      struct Message m = {m_no_flags_flag, d->device_id, data_size, data};
      send_message(&m);  
    }  
  }

  // If we are an initialized actuator and the incoming message is complete and a normal one and referred to this device
  // We read the incoming data and actuate them!
  if(d->state == initialized && 
     d->actuator_func != NULL && 
     reading_input_result == message_done && 
     in_buffer -> flags == m_no_flags_flag &&
     in_buffer -> device_id == d-> device_id){
      d->actuator_func(in_buffer -> data);      
  }
  return idling; // I tell to the microcontroller that i do not need any special reservation to the in_buffer!
}



#define buffer_size 254 // well in case i needed to write in more places and update it quickly
void controller_loop(Device* devices, unsigned char n_devices)
{
  static char* buffer[buffer_size] = {0}; // I'm initializing it to 0 but it does not really make a huge difference
  static struct Message mc_input_buffer = new_empty_message(buffer); 
  static enum controller_com_state com_state = idling;

  char read_return_result = read_input(&mc_input_buffer); // I read the input and save the result of the read
  for(unsigned char i = 0; i < n_devices; i++){
    enum controller_com_state new_state = device_run(devices + i, &mc_input_buffer, com_state, read_return_result);
  
    if(com_state == idling)
      com_state = new_state;
    if(com_state == initializing_device && new_state == initialization_finished)
      com_state = idling;
  }
}

//void mc_loop(int (*data_collector) (char* data_buffer))
