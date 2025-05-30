#ifndef __CONSTANTS_INC__
#define __CONSTANTS_INC__

/* 
 *  This file containts all the packet types, commands
 *  and status constants
 *  
 */

// Packet types
typedef enum {
  PACKET_TYPE_COMMAND = 0,
  PACKET_TYPE_RESPONSE = 1,
  PACKET_TYPE_ERROR = 2,
  PACKET_TYPE_MESSAGE = 3,
  PACKET_TYPE_HELLO = 4
} TPacketType;

// Response types. This goes into the command field
typedef enum {
  RESP_OK = 0,
  RESP_STATUS = 1,
  RESP_BAD_PACKET = 2,
  RESP_BAD_CHECKSUM = 3,
  RESP_BAD_COMMAND = 4,
  RESP_BAD_RESPONSE = 5,
  RESP_COLOR = 6,
} TResponseType;


// Commands
// For direction commands, param[0] = distance in cm to move
// param[1] = speed
typedef enum {
  COMMAND_FORWARD = 0,
  COMMAND_REVERSE = 1,
  COMMAND_TURN_LEFT = 2,
  COMMAND_TURN_RIGHT = 3,
  COMMAND_STOP = 4,
  COMMAND_GET_STATS = 5,
  COMMAND_CLEAR_STATS = 6,
  COMMAND_OPEN_CLAW = 7,
  COMMAND_CLOSE_CLAW = 8,
  COMMAND_GET_COLOR = 9,
  COMMAND_OPEN_SMALL_CLAW = 10,
  COMMAND_CLOSE_SMALL_CLAW = 11,
} TCommandType;

// the names FORWARD and BACKWARD are defined by the adafruit library as 1 and 2 respectively
// so the same values are used to avoid any issues
typedef enum {
  FORWARD = 1,
  BACKWARD = 2,
  LEFT = 3,
  RIGHT = 4,
  STOP = 5
} TDirection;

typedef enum {
  RED = 0,
  GREEN = 1,
  UNKNOWN = 2,
} Tcolor;
#endif