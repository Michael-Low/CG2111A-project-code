import asyncio
from websockets.asyncio.client import connect
import queue
from dataclasses import dataclass, field

_rx_queue = queue.Queue()

@dataclass
class MapPose:
    x: float
    y: float
    thetaRad: float
    mapbytes: bytearray

async def recv():
    async with connect("ws://raspberrypi.local:8766") as ws:
        while True:
            x = await ws.recv()
            y = await ws.recv()
            thetaRad = await ws.recv()
            mapbytes = await ws.recv()
            newMapPose = MapPose(x=float(x), y=float(y), thetaRad=float(thetaRad), mapbytes=mapbytes)
            _rx_queue.put(newMapPose)


if(__name__ == "__main__"):
    asyncio.run(recv())