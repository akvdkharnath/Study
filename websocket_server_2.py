from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import websockets
from typing import Dict, List
import uvicorn

app = FastAPI(title="FastAPI Server 2 - WebSocket Example")

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.server1_connection = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def connect_to_server1(self):
        """Connect to Server 1 as a WebSocket client"""
        try:
            uri = "ws://localhost:8000/ws"
            self.server1_connection = await websockets.connect(uri)
            print("Connected to Server 1")
            return True
        except Exception as e:
            print(f"Failed to connect to Server 1: {e}")
            return False

    async def send_to_server1(self, message: str):
        """Send message to Server 1"""
        if self.server1_connection:
            await self.server1_connection.send(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Server 2 - WebSocket Test</title>
        </head>
        <body>
            <h1>Server 2 WebSocket Test</h1>
            <div id="messages"></div>
            <input type="text" id="messageText" placeholder="Type a message...">
            <button onclick="sendMessage()">Send to Server 1</button>
            <button onclick="connectToServer1()">Connect to Server 1</button>
            <script>
                var ws = new WebSocket("ws://localhost:8001/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('div');
                    message.textContent = event.data;
                    messages.appendChild(message);
                };
                function sendMessage() {
                    var input = document.getElementById('messageText');
                    ws.send(input.value);
                    input.value = '';
                }
                function connectToServer1() {
                    fetch('/connect-server1');
                }
            </script>
        </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Server 2 received: {data}")
            
            # Echo back to client
            await manager.send_personal_message(f"Echo: {data}", websocket)
            
            # Forward to Server 1 if connected
            await manager.send_to_server1(f"From Server 2: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/connect-server1")
async def connect_to_server1():
    """Endpoint to establish connection with Server 1"""
    success = await manager.connect_to_server1()
    return {"status": "connected" if success else "failed"}

@app.post("/send-to-server1")
async def send_to_server1(message: str):
    """Endpoint to send message to Server 1"""
    await manager.send_to_server1(message)
    return {"status": "sent"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
