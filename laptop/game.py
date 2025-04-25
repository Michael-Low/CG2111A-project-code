import numpy as np
import asyncio
from websockets.asyncio.client import connect
import websockets
import pygame
from pygame.locals import *
from enum import Enum
import threading
import queue
from dataclasses import dataclass, field
import time

BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GAME_WIDTH = 1000
GAME_HEIGHT = 1000
WS_SERVER = "raspberrypi.local"
# WS_SERVER = "172.23.144.103"
ENABLE_MAP = True

_tx_queue = queue.LifoQueue()
_rx_queue = queue.Queue()
_is_running = threading.Event()

@dataclass
class MapPose:
    x: float
    y: float
    thetaDeg: float
    mapbytes: bytearray

class Dir(Enum):
    STOP = 0
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

def main():
    _is_running.set()
    gameThread = threading.Thread(target = game)
    commandThread = threading.Thread(target=run_command_client)
    recvThread = threading.Thread(target=run_recv_client)
    commandThread.start()
    if ENABLE_MAP: recvThread.start()
    gameThread.start()
    commandThread.join()
    if ENABLE_MAP: recvThread.join()
    gameThread.join()

def run_command_client():
    asyncio.run(start_command_client())

async def start_command_client():
    command_task = asyncio.create_task(command_client())
    while _is_running.is_set():
        await asyncio.sleep(1)
    command_task.cancel()

def run_recv_client():
    asyncio.run(start_recv_client())

async def start_recv_client():
    recv_task = asyncio.create_task(recv_client())
    while _is_running.is_set():
        await asyncio.sleep(1)
    recv_task.cancel()

async def recv_client():
    async def recv_map(ws):
        x = await ws.recv()
        y = await ws.recv()
        thetaDeg = await ws.recv()
        mapbytes = await ws.recv()
        return MapPose(x=float(x), y=float(y), 
                       thetaDeg=float(thetaDeg), 
                       mapbytes=mapbytes)
    
    async def recv_color(ws):
        color = await ws.recv()
        red = await ws.recv()
        green = await ws.recv()
        blue = await ws.recv()
        return ("color", color, red, green, blue)
    
    async with connect(f"ws://{WS_SERVER}:8766") as ws:
        print("Receiving client connected")
        try:
            await ws.recv()
            await ws.send("hi")
            while True:
                message_type = await ws.recv()
                if(message_type == "map"):
                    newMapPose = await recv_map(ws)
                    _rx_queue.put(("map", newMapPose))
                elif(message_type == "color"):
                    _rx_queue.put(await recv_color(ws))
                await ws.send("received")
        except websockets.exceptions.ConnectionClosed:
            print("Receiving WS connection closed")
        except Exception as e:
            print(f"Receiving WS connection exception: {e}")
        finally:
            _is_running.clear()

async def command_client():
    async with connect(f"ws://{WS_SERVER}:8765") as ws:
        print("Command client connected")
        try:
            while True:
                if not _tx_queue.empty():
                    # _tx_queue is a LiFo queue so only the last command will be transmitted
                    command = _tx_queue.get()
                    await ws.send(command)
                    while not _tx_queue.empty():
                        # remove all previous commands that may have been backed up
                        # due to bad connection, etc
                        _tx_queue.get()
                    reply = await ws.recv()
                    print(reply)
                else:
                    await asyncio.sleep(0.05)
        except websockets.exceptions.ConnectionClosed:
            print("Command WS connection closed")
        finally:
            _is_running.clear()

def mapBytesToGrid(mapbytes, width, height):
    """
    Converts a byte array representing a map to a 2D grid. 
    The positve Y-axis is assumed to be north (i.e., front)
    The positive X-axis is assumed to be east (i.e., right)

    Args:
        map_bytes (bytes): The byte array representing the map.
        width (int): The width of the map.
        height (int): The height of the map.

    Returns:
        list: A 2D grid representing the map.
    """
    mapimg = np.reshape(np.frombuffer(mapbytes, dtype=np.uint8), (width, height), order="C").astype(int, casting="safe")
    mapimg = mapimg.T
    mapimg = mapimg.repeat(2, axis=0).repeat(2, axis=1)
    return np.repeat(mapimg[:, :, np.newaxis], 3, axis=2)

def scale_coordinates(x, y):
    return ((8000 - x) * GAME_WIDTH / 8000, (8000 - y) * GAME_HEIGHT / 8000)

def get_line_end(x, y, len, thetaDeg):
    return (x - len * np.cos(thetaDeg * np.pi / 180), y + len * np.sin(thetaDeg * np.pi / 180))

def check_wsad(curKeys):
    if(curKeys[K_w]):
        return ("f", Dir.FORWARD)
    elif(curKeys[K_s]):
        return ("b", Dir.BACKWARD)
    elif(curKeys[K_a]):
        return ("l", Dir.LEFT)
    elif(curKeys[K_d]):
        return ("r", Dir.RIGHT)
    return ("s", Dir.STOP)

def game():
    dir = Dir.STOP
    DISPLAYSURF = pygame.display.set_mode((GAME_WIDTH,GAME_HEIGHT))
    pygame.display.set_caption("Test")
    pygame.init()
    clock = pygame.time.Clock()
    targetTime = time.time() * 1000
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', 20)
    map_count = 0
    color = "unknown"
    red, green, blue = 0, 0, 0
    color_count = 0
    has_map = False
    claw_state = "unknown"
    small_claw_state = "unknown"
    try:
        while _is_running.is_set():
            DISPLAYSURF.fill(WHITE)
            curKeys = pygame.key.get_pressed()
            curTime = time.time() * 1000
            command, nextDir = check_wsad(curKeys)
            if not (dir == nextDir):
                targetTime = curTime + 200
                _tx_queue.put(command)
                dir = nextDir
            elif (not (dir == Dir.STOP)) and targetTime < curTime: 
                targetTime = curTime + 200
                _tx_queue.put(command)
            
            for event in pygame.event.get():
                if(event.type == QUIT):
                    _is_running.clear()
                elif(event.type == KEYDOWN and dir == Dir.STOP):
                    if event.key == K_f:
                        _tx_queue.put("color")
                    elif event.key == K_i:
                        _tx_queue.put("open")
                        claw_state = "open"
                    elif event.key == K_o:
                        _tx_queue.put("close")
                        claw_state = "close"
                    elif event.key == K_r:
                        _tx_queue.put("creep")
                    elif event.key == K_k:
                        _tx_queue.put("open small")
                        small_claw_state = "open"
                    elif event.key == K_l:
                        _tx_queue.put("close small")
                        small_claw_state = "close"
                    elif event.key == K_q:
                        _tx_queue.put("creep left")
                    elif event.key == K_e:
                        _tx_queue.put("creep right")
            while(not _rx_queue.empty()):
                message = _rx_queue.get()
                if(message[0] == "map"):
                    has_map = True
                    map_pose = message[1]
                    map_count += 1
                    # process map data
                    grid = mapBytesToGrid(map_pose.mapbytes, width=500, height=500)
                    scaled_x, scaled_y = scale_coordinates(map_pose.x, map_pose.y)
                elif(message[0] == "color"):
                    color, red, green, blue = message[1], int(message[2]), int(message[3]), int(message[4])
                    color_count += 1
            if has_map == True:
                pygame.surfarray.blit_array(DISPLAYSURF,grid)
                end_x, end_y = get_line_end(scaled_x, scaled_y, len=32,
                                            thetaDeg=map_pose.thetaDeg)
                line_color = pygame.Color(BLUE[0], BLUE[1], BLUE[2], 100)
                pygame.draw.line(surface=DISPLAYSURF,
                                color=line_color,
                                start_pos=(scaled_y, scaled_x),
                                end_pos=(end_y, end_x),
                                width=3)
                pygame.draw.circle(surface=DISPLAYSURF, 
                                color=RED,radius=6,
                                center=(scaled_y, scaled_x))
            text_surface = font.render(f'Map number: {map_count}, small claw: {small_claw_state}, big claw: {claw_state}', False, BLACK)
            color_text_surface = font.render(f'Color {color_count}: {color}, red = {red}, green = {green}, blue = {blue}', False, BLACK)
            DISPLAYSURF.blit(text_surface, (0, 0))
            DISPLAYSURF.blit(color_text_surface, (0, 25))
            pygame.display.update()
            clock.tick(20)
    except Exception as e:
        print(f"Exception in game loop: {e}")
    finally:
        _is_running.clear()
if __name__ == "__main__":
    main()