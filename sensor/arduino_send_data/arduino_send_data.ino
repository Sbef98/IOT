// get data from arduino sensors and send them via the serial port
unsigned long lasttime;
int iState;

int sensorValue1 = 0;        // value1
int sensorValue2 = 0;        // value2


void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  lasttime=millis();
}

void loop() {

  // read every 5 sec
  if (millis() - lasttime > 5000)
  {
    lasttime = millis();
        
    // read the analog in values:
    //sensorValue1 = analogRead(analogInPin1);
    //sensorValue2 = analogRead(analogInPin2);

    //sending hard coded data
    sensorValue1 = 111;
    sensorValue2 = 123;
   
    // print the results to the Serial Monitor:
    Serial.write(0xff);
    Serial.write(0x02);
    Serial.write((char)(map(sensorValue1,0,1024,0,253)));
    Serial.write((char)(map(sensorValue2,0,1024,0,253)));
    Serial.write(0xfe);

  } 
  

  int iFutureState;
  int iReceived;

  if (Serial.available()>0)
  { 
    iReceived = Serial.read();

    // default: back to the first state
    iFutureState=0;

    if (iState==0 && iReceived=='O') iFutureState=1;
    if (iState==1 && iReceived=='N') iFutureState=2;
    if (iState==1 && iReceived=='F') iFutureState=3;
    if (iState==3 && iReceived=='F') iFutureState=4;
    if (iState==4 && iReceived=='O') iFutureState=1;
    if (iState==2 && iReceived=='O') iFutureState=1;
    
    // CR and LF always skipped (no transition)
    if (iReceived==10 || iReceived==13) iFutureState=iState;

     // onEnter Actions
    
     if (iFutureState==2 && iState==1) digitalWrite(13, HIGH);  // switch on from 1 to 2
     if (iFutureState==4 && iState==3) digitalWrite(13, LOW);  // switch off from 3 to 4
     
     // state transition
     iState = iFutureState;

     // Moore outputs
     // NO ADDITIONAL OUTPUTS

   
  }

}
