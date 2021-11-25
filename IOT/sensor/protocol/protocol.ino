//#include  "protocol.h"
//////////////////////// GLOBAL VARS //////////////////////////////

int data_collector1 (char* data_buffer){
  Serial.println("ciao mamma");
}
int data_collector2 (char* data_buffer){
  Serial.println("ciao");
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  char* tt[2] = {(char*)data_collector1, (char*)data_collector2}; // This is some toxic stuff but idk how to do it better than this
  int (*func1) (char* data_buffer) = (int (*)(char*))tt[1];
  int (*func2) (char* data_buffer) = (int (*)(char*))tt[0];
  char c[2] = {'t',0};
  func1(c);
  func2(c);
  delay(1000);
}
