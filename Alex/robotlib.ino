#include <AFMotor.h>
// Direction values


// Motor control
#define FRONT_LEFT   2 // M2 on the driver shield
#define FRONT_RIGHT  1 // M1 on the driver shield
#define BACK_LEFT    3 // M3 on the driver shield
#define BACK_RIGHT   4 // M4 on the driver shield

AF_DCMotor motorFL(FRONT_LEFT);
AF_DCMotor motorFR(FRONT_RIGHT);
AF_DCMotor motorBL(BACK_LEFT);
AF_DCMotor motorBR(BACK_RIGHT);

void move(float speed, int direction)
{
  int speed_scaled = (speed/100.0) * 255;
  motorFL.setSpeed(speed_scaled);
  motorFR.setSpeed(speed_scaled);
  motorBL.setSpeed(speed_scaled);
  motorBR.setSpeed(speed_scaled);

  switch(direction)
    {
      case BACKWARD:
        motorFL.run(BACKWARD);
        motorFR.run(FORWARD);
        motorBL.run(BACKWARD);
        motorBR.run(FORWARD); 
      break;
      case FORWARD:
        motorFL.run(FORWARD);
        motorFR.run(BACKWARD);
        motorBL.run(FORWARD);
        motorBR.run(BACKWARD); 
      break;
      case LEFT:
        motorBR.run(FORWARD); 
        motorFL.run(FORWARD);
        motorFR.run(FORWARD);
        motorBL.run(FORWARD);
      break;
      case RIGHT:
        motorFL.run(BACKWARD);
        motorFR.run(BACKWARD);
        motorBL.run(BACKWARD);
        motorBR.run(BACKWARD);
      break;
      case STOP:
      default:
        motorFL.run(BRAKE);
        motorFR.run(BRAKE);
        motorBL.run(BRAKE);
        motorBR.run(BRAKE); 
    }
}

long computeDeltaTicks(float angle) {
  return (angle > 0) ? (angle * TICKS_PER_90DEG / 90) : 9999;
}

void forward(int time, float speed)
{
  stop_time = millis() + time;
  dir = FORWARD;
  move(speed, FORWARD);
}

void backward(int time, float speed)
{ 
  stop_time = millis() + time;
  dir = BACKWARD;
  move(speed, BACKWARD);
}

void left(int time, float speed)
{
  stop_time = millis() + time;
  dir = LEFT;
  move(speed, LEFT);
}

void right(int time, float speed)
{
  stop_time = millis() + time;
  dir = RIGHT;
  move(speed, RIGHT);
}

void stop()
{
  dir = STOP;
  move(0, STOP);
}
