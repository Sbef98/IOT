// So this is basically the states for reading any message through our protocol
typedef enum {
  message_begin,
  flags_read,
  sensor_id_read,
  data_size_read,
  data_reading,
  message_end
} Reading_states;

// This is the states that our sensors could be set to.
typedef enum {
  not_initialized;
  initialized;
} Sensor_state;

// This is the states that our arduino communication can be set to
typedef enum {
  idling; //when we can get an input
  initializing; // WHen reading input data from serial to initialize a sensors
} Arduino_states;

Sensor_state s_state = not_initialized;
//Note: basically all my parameters in the functions are passed by reference,
//avoiding the passage via copy so that we do not slow down the ugli duino thingy thing

void rading_input

void initialization(char* message, Reading_states* message_state){
}

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}
