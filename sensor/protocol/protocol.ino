#include  "protocol.h"
//////////////////////// GLOBAL VARS //////////////////////////////


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  struct Message m;
  m.flags = 0;
  m.sensor_id = 0;
  m.data_size = 1;
  m.data[0] = 'c';
  enum Reading_states f_m_state = message_begin;
  send_message(&m);
  delay(100);
}
