#include <Servo.h>

Servo myservo;  // create servo object to control a servo
Servo s2;
Servo smallclaw;


closeSmallClaw(){
  smallclaw.write(90);
}

openSmallClaw(){
  smallclaw.write(0);  // tell servo to go to a particular 
}

void setupServo() {
  smallclaw.attach (42,600,2300);
  myservo.attach(9,600,2300);  // (pin, min, max)
  s2.attach(10,600,2300);  // (pin, min, max)
  closeClaw();
  closeSmallClaw();
}

void closeClaw(){
  myservo.write(45);
  s2.write(30);
}

void openClaw(){
  myservo.write(0);  // tell servo to go to a particular angle
  s2.write(90);
}