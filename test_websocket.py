import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:5000/ws"

    async with websockets.connect(uri) as websocket:
        try:
            # Send a message
            message = "what is the temperature in New York city"
            await websocket.send(message)
            print(f"Sent: {message}")

            # Receive response
            response = await websocket.recv()
            print(f"Received: {response}")

        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
