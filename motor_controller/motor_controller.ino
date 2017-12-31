#include <Stepper.h>

#define BUFFER_SIZE 64
#define STEPS_PER_READ 10

long positions[2];
typedef enum {FORWARD = 0, REVERSE = 1} direction_t;

Stepper left_stepper(200, 4, 5);
Stepper right_stepper(200, 2, 3);

inline int sgn(int a) {
  if (a < 0) return -1;
  else if (a > 0) return 1;
  else return 0;
}

int parse(int* left_rpm, int* right_rpm) {
  // message format:left_rpm right_rpm \n
  char buffer[BUFFER_SIZE + 1];
  byte size = Serial.readBytes(buffer, BUFFER_SIZE);
  buffer[size] = '\0';
  int i = 0;
  char* tok = strtok(buffer, " ");
  while (tok != 0) {
    int val = atoi(tok);
    switch (i) {
      case 0:
        *left_rpm = val;
      case 1:
        *right_rpm = val;
    }
    i++;
    tok = strtok(0, " ");
  }
  // success requires that only 4 tokens were found
  return size;
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50); // lowers serial latency
}

int left_rpm = 0;
int right_rpm = 0;

void loop() {
 if (Serial.available()) {
   int parse_success = parse(&left_rpm, &right_rpm);
   Serial.println(parse_success);
   left_stepper.setSpeed(abs(left_rpm));
   right_stepper.setSpeed(abs(right_rpm));
 }

 for (int i = 0; i < STEPS_PER_READ; i++) {
   right_stepper.step(-sgn(right_rpm));
   left_stepper.step(sgn(left_rpm));
 }
}
