import asyncio
import websockets
import json
from typing import Dict, Any

class WebSocketClient:
    def __init__(self, uri: str, name: str):
        self.uri = uri
        self.name = name
        self.websocket = None
        self.connected = False

    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print(f"{self.name} connected to {self.uri}")
            return True
        except Exception as e:
            print(f"{self.name} connection failed: {e}")
            return False

    async def send_message(self, message: str):
        """Send message to server"""
        if self.connected and self.websocket:
            await self.websocket.send(message)
            print(f"{self.name} sent: {message}")

    async def listen(self):
        """Listen for incoming messages"""
        if self.connected and self.websocket:
            try:
                async for message in self.websocket:
                    print(f"{self.name} received: {message}")
            except websockets.exceptions.ConnectionClosed:
                print(f"{self.name} connection closed")
                self.connected = False

    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print(f"{self.name} disconnected")

async def bidirectional_communication_demo():
    """Demonstrate bidirectional communication between two servers"""
    
    # Create clients for both servers
    server1_client = WebSocketClient("ws://localhost:8000/ws", "Client-to-Server1")
    server2_client = WebSocketClient("ws://localhost:8001/ws", "Client-to-Server2")
    
    # Connect to both servers
    await server1_client.connect()
    await server2_client.connect()
    
    if not server1_client.connected or not server2_client.connected:
        print("Failed to connect to one or both servers")
        return
    
    # Start listening tasks
    listen_task1 = asyncio.create_task(server1_client.listen())
    listen_task2 = asyncio.create_task(server2_client.listen())
    
    try:
        # Send messages between servers
        for i in range(5):
            await server1_client.send_message(f"Hello from Server 1 - Message {i+1}")
            await asyncio.sleep(1)
            
            await server2_client.send_message(f"Hello from Server 2 - Message {i+1}")
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("Demo interrupted by user")
    
    finally:
        # Clean up
        listen_task1.cancel()
        listen_task2.cancel()
        await server1_client.disconnect()
        await server2_client.disconnect()

async def server_to_server_demo():
    """Demonstrate server-to-server communication"""
    
    # This would be used within a server to connect to another server
    server2_client = WebSocketClient("ws://localhost:8001/ws", "Server1-to-Server2")
    
    await server2_client.connect()
    
    if server2_client.connected:
        # Send messages from Server 1 to Server 2
        for i in range(3):
            await server2_client.send_message(f"Server-to-Server message {i+1}")
            await asyncio.sleep(2)
        
        await server2_client.disconnect()

if __name__ == "__main__":
    print("WebSocket Bidirectional Communication Demo")
    print("Make sure both servers are running:")
    print("  Server 1: python server1.py (port 8000)")
    print("  Server 2: python server2.py (port 8001)")
    print("\nStarting demo in 3 seconds...")
    
    asyncio.sleep(3)
    asyncio.run(bidirectional_communication_demo())
