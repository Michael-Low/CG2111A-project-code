import asyncio
from websockets.asyncio.server import serve
import websockets
from threading import Barrier
from control.alex_control_constants import TCommandType, TPacketType

# Import the required pubsub modules. PubSubMsg class to extract the payload from a message.
from pubsub.pub_sub_manager import ManagedPubSubRunnable, PubSubMsg
from pubsub.pub_sub_manager import publish, subscribe, unsubscribe, getMessages, getCurrentExecutionContext  

# Constants
WEBSOCKET_RECV_TOPIC = "websocket/recv"
ARDUINO_SEND_TOPIC = "arduino/send"

def websocketThread(setupBarrier:Barrier=None, readyBarrier:Barrier=None):
    ctx:ManagedPubSubRunnable = getCurrentExecutionContext()

    # Perform any setup here
    setupBarrier.wait() if readyBarrier != None else None

    print("starting websocket server")

    # Wait for all Threads ready
    readyBarrier.wait() if readyBarrier != None else None
    asyncio.run(server(ctx))
    
    ctx.doExit()
    print("Exiting Websocket Recv Thread")

async def server(ctx):
    server_task = asyncio.create_task(start_server())
    
    while not ctx.isExit():
        await asyncio.sleep(1)
    server_task.cancel()

async def echo(websocket):
    print("New connection established.")
    try:
        while True:
            message = await websocket.recv()
            match message:
                case "f":
                    command = TCommandType.COMMAND_FORWARD
                case "b":
                    command = TCommandType.COMMAND_REVERSE
                case "l":
                    command = TCommandType.COMMAND_TURN_LEFT
                case "r":
                    command = TCommandType.COMMAND_TURN_RIGHT
                case "s":
                    command = TCommandType.COMMAND_STOP
            commandPacket = (TPacketType.PACKET_TYPE_COMMAND, command, 100)
            publish(ARDUINO_SEND_TOPIC, commandPacket)
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed.")

async def start_server():
    server = await serve(echo, "", 8765)
    await server.serve_forever()