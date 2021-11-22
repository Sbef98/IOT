#include  "protocol.h"
//////////////////////// GLOBAL VARS //////////////////////////////


void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:
  struct Message m;
  m.flags = 0;
  m.sensor_id = 0;
  m.data_size = 1;
  m.data[0] = 1;
  enum Reading_states f_m_state = message_begin;
  send_message(&m);
}
