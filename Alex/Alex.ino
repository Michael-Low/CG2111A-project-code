#include "serialize.h"
#include "packet.h"
#include "constants.h"
#include <stdarg.h>

/*
 * Alex's configuration constants
 */

// Number of ticks per revolution from the
// wheel encoder.

#define COUNTS_PER_REV 4

// Wheel circumference in cm.
// We will use this to calculate forward/backward distance traveled
// by taking revs * WHEEL_CIRC

#define WHEEL_CIRC 17

#define TICKS_PER_90DEG 20
/*
 *    Alex's State Variables
 */

// Store the ticks from Alex's left and
// right encoders.
volatile long leftTicks = 0;
volatile long rightTicks = 0;

volatile int dir = STOP;
// Forward and backward distance traveled
volatile long dist = 0;

volatile long stop_time = 0;

/*
 * Setup and start codes for external interrupts and 
 * pullup resistors.
 * 
 */
// Enable pull up resistors on pins 18 and 19
void enablePullups() {
  // Use bare-metal to enable the pull-up resistors on pins
  // 19 and 18. These are pins PD2 and PD3 respectively.
  // We set bits 2 and 3 in DDRD to 0 to make them inputs.
  DDRD &= 0X00;
  PORTD |= 0b00001100;
}

// Functions to be called by INT2 and INT3 ISRs.
void leftISR() {
  if (dir == FORWARD || dir == RIGHT) {
    leftTicks++;
  } else if (dir == BACKWARD || dir == LEFT) {
    leftTicks--;
  }
  dist = (leftTicks * WHEEL_CIRC / COUNTS_PER_REV);
}

void rightISR() {
  if (dir == FORWARD || dir == LEFT) {
    rightTicks++;
  } else if (dir == BACKWARD || dir == RIGHT) {
    rightTicks--;
  }
}

// Set up the external interrupt pins INT2 and INT3
// for falling edge triggered. Use bare-metal.
void setupEINT() {
  // Use bare-metal to configure pins 18 and 19 to be
  // falling edge triggered. Remember to enable
  // the INT2 and INT3 interrupts.
  // Hint: Check pages 110 and 111 in the ATmega2560 Datasheet.
  EICRA = 0B10100000;
  EIMSK |= 0B00001100;
}

// Implement the external interrupt ISRs below.
// INT3 ISR should call leftISR while INT2 ISR
// should call rightISR.

ISR(INT3_vect) {
  leftISR();
}

ISR(INT2_vect) {
  rightISR();
}

/*
 * Alex's setup and run codes
 * 
 */

// Clears all our counters
void clearCounters() {
  leftTicks = 0;
  rightTicks = 0;
  dist = 0;
}

// Clears one particular counter
void clearOneCounter(int which) {
  clearCounters();
}
// Intialize Alex's internal states
void initializeState() {
  clearCounters();
}

void handleCommand(TPacket *command) {
  switch (command->command) {
    // For movement commands, param[0] = distance, param[1] = speed.
    case COMMAND_FORWARD:
      forward(command->params[0], (float)command->params[1]);
      break;
    case COMMAND_REVERSE:
      backward(command->params[0], (float)command->params[1]);
      break;
    case COMMAND_TURN_LEFT:
      left(command->params[0], (float)command->params[1]);
      break;
    case COMMAND_TURN_RIGHT:
      right(command->params[0], (float)command->params[1]);
      break;
    case COMMAND_STOP:
      stop();
      break;
    case COMMAND_GET_STATS:
      sendStatus();
      break;
    case COMMAND_CLEAR_STATS:
      clearOneCounter(command->params[0]);
      break;
    case COMMAND_CLOSE_CLAW:
      closeclaw();
      break;
    case COMMAND_OPEN_CLAW:
      openclaw();
      break;
    case COMMAND_GET_COLOR:
      findColor();
      sendColor(processcolor());
      //TODO: implement
      break;
    default:
      sendBadCommand();
  }
}

void setup() {
  // put your setup code here, to run once:

  cli();
  setupServo();
  setupEINT();
  setupSerial();
  startSerial();
  enablePullups();
  initializeState();
  setupColor();
  sei();
}

void handlePacket(TPacket *packet) {
  switch (packet->packetType) {
    case PACKET_TYPE_COMMAND:
      handleCommand(packet);
      break;

    case PACKET_TYPE_RESPONSE:
      break;

    case PACKET_TYPE_ERROR:
      break;

    case PACKET_TYPE_MESSAGE:
      break;

    case PACKET_TYPE_HELLO:
      break;
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  TPacket recvPacket;  // This holds commands from the Pi

  TResult result = readPacket(&recvPacket);

  if (result == PACKET_OK)
    handlePacket(&recvPacket);
  else if (result == PACKET_BAD) {
    sendBadPacket();
  } else if (result == PACKET_CHECKSUM_BAD) {
    sendBadChecksum();
  }

  if (dir != STOP) {
    if(millis() > stop_time) {
      stop();
    }
  }
}
