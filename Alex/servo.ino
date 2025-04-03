#include <Servo.h>

Servo myservo;  // create servo object to control a servo
Servo s2;

void setupServo() {
  myservo.attach(9,600,2300);  // (pin, min, max)
  s2.attach(10,600,2300);  // (pin, min, max)
}

void closeclaw(){
  myservo.write(45);
  s2.write(30);  
}

void openclaw(){
  myservo.write(0);  // tell servo to go to a particular angle
  s2.write(90);
}