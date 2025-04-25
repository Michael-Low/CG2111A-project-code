#!/usr/bin/env python

"""Echo server using the asyncio API."""

import asyncio
import websockets
from websockets.asyncio.server import serve

async def echo(websocket):
    print("New connection established.")
    try:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed.")

async def start_server():
    server = await serve(echo, "localhost", 8765)
    await server.serve_forever()

async def main():
    print("starting server")
    server_task = asyncio.create_task(start_server())
    print("done")

if __name__ == "__main__":
    asyncio.run(main())