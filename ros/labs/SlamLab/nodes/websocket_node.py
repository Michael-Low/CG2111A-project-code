import asyncio
from websockets.asyncio.server import serve
import websockets
from threading import Barrier
from control.alex_control_constants import TCommandType, TPacketType

# Import the required pubsub modules. PubSubMsg class to extract the payload from a message.
from pubsub.pub_sub_manager import ManagedPubSubRunnable, PubSubMsg
from pubsub.pub_sub_manager import publish, subscribe, unsubscribe, getMessages, getCurrentExecutionContext  

# Constants
ARDUINO_SEND_TOPIC = "arduino/send"
SLAM_MAPPOSE_TOPIC = "slam/mappose"
COLOR_SENSOR_TOPIC = "sensor/color"

def websocketThread(setupBarrier:Barrier=None, readyBarrier:Barrier=None):
    ctx:ManagedPubSubRunnable = getCurrentExecutionContext()

    # Perform any setup here
    setupBarrier.wait() if readyBarrier != None else None
    print("starting websocket server")
    subscribe(topic=SLAM_MAPPOSE_TOPIC, ensureReply=True, replyTimeout=1)
    subscribe(topic=COLOR_SENSOR_TOPIC, ensureReply=True, replyTimeout=1)

    # Wait for all Threads ready
    readyBarrier.wait() if readyBarrier != None else None
    asyncio.run(server(ctx))
    
    ctx.doExit()
    print("Exiting Websocket Thread")

async def server(ctx):
    recv_server_task = asyncio.create_task(start_command_server())
    map_server_task = asyncio.create_task(start_map_server())
    while not ctx.isExit():
        await asyncio.sleep(1)
    recv_server_task.cancel()
    map_server_task.cancel()

async def start_command_server():
    server = await serve(recv_commands, "", 8765)
    await server.serve_forever()

async def start_map_server():
    server = await serve(send_map_data, "", 8766)
    await server.serve_forever()

async def send_map_data(websocket):
    async def sendColor(message, ws):
        color, redFreq, greenFreq, blueFreq = PubSubMsg.getPayload(message)
        await ws.send("color")
        await ws.send(color)
        await ws.send(redFreq)
        await ws.send(greenFreq)
        await ws.send(blueFreq)
        await ws.recv()
    
    async def sendMap(message, ws):
        x, y, theta, mapbytes = PubSubMsg.getPayload(message)
        await ws.send("map")
        await ws.send(str(x))
        await ws.send(str(y))
        await ws.send(str(theta))
        await ws.send(mapbytes)
        await ws.recv()

    print("Sending websocket connection established.")
    try:
        await websocket.send("hi")
        await websocket.recv()
        while True:
            messages = getMessages()
            map_messages = PubSubMsg.filterMessages(messages, SLAM_MAPPOSE_TOPIC)
            color_messages = PubSubMsg.filterMessages(messages, COLOR_SENSOR_TOPIC)
            if(len(map_messages) > 0):
                await sendMap(map_messages[-1], websocket)
            if(len(color_messages) > 0):
                await sendColor(color_messages[-1], websocket)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Map WS exception: {e}")
    finally:
        print("Map WS connection closed.")

async def recv_commands(websocket):
    params = [0] * 16
    print("Receiving websocket connection established.")
    try:
        while True:
            message = await websocket.recv()
            print(f"Command received: {message}")
            match message:
                case "f":
                    params[0] = 200
                    params[1] = 50
                    command = TCommandType.COMMAND_FORWARD
                case "b":
                    params[0] = 200
                    params[1] = 50
                    command = TCommandType.COMMAND_REVERSE
                case "l":
                    params[0] = 200
                    params[1] = 100
                    command = TCommandType.COMMAND_TURN_LEFT
                case "r":
                    params[0] = 200
                    params[1] = 100
                    command = TCommandType.COMMAND_TURN_RIGHT
                case "s":
                    command = TCommandType.COMMAND_STOP
                case "color":
                    command = TCommandType.COMMAND_GET_COLOR
                case "open":
                    command = TCommandType.COMMAND_OPEN_CLAW
                case "close":
                    command = TCommandType.COMMAND_CLOSE_CLAW
                case "creep left":
                    params[0] = 50
                    params[1] = 100
                    command = TCommandType.COMMAND_TURN_LEFT
                case "creep right":
                    params[0] = 50
                    params[1] = 100
                    command = TCommandType.COMMAND_TURN_RIGHT
                case "creep":
                    params[0] = 50
                    params[1] = 50
                    command = TCommandType.COMMAND_FORWARD
                case "open small":
                    command = TCommandType.COMMAND_OPEN_SMALL_CLAW
                case "close small":
                    command = TCommandType.COMMAND_CLOSE_SMALL_CLAW
            commandPacket = (TPacketType.PACKET_TYPE_COMMAND, command, params)
            publish(ARDUINO_SEND_TOPIC, commandPacket)
            await websocket.send(f"Echo: {message}")
    except Exception as e:
        print(f"Command WS exception: {e}")
    finally:
        commandPacket = (TPacketType.PACKET_TYPE_COMMAND, TCommandType.COMMAND_STOP, params)
        publish(ARDUINO_SEND_TOPIC, commandPacket)
        print("Stopping robot, websockets connection closed")