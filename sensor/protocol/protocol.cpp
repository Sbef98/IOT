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
