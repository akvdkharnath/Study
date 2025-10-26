from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import websockets
from typing import Dict, List
import uvicorn

app = FastAPI(title="FastAPI Server 1 - WebSocket Example")

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.server2_connection = None

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

    async def connect_to_server2(self):
        """Connect to Server 2 as a WebSocket client"""
        try:
            uri = "ws://localhost:8001/ws"
            self.server2_connection = await websockets.connect(uri)
            print("Connected to Server 2")
            return True
        except Exception as e:
            print(f"Failed to connect to Server 2: {e}")
            return False

    async def send_to_server2(self, message: str):
        """Send message to Server 2"""
        if self.server2_connection:
            await self.server2_connection.send(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Server 1 - WebSocket Test</title>
        </head>
        <body>
            <h1>Server 1 WebSocket Test</h1>
            <div id="messages"></div>
            <input type="text" id="messageText" placeholder="Type a message...">
            <button onclick="sendMessage()">Send to Server 2</button>
            <button onclick="connectToServer2()">Connect to Server 2</button>
            <script>
                var ws = new WebSocket("ws://localhost:8000/ws");
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
                function connectToServer2() {
                    fetch('/connect-server2');
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
            print(f"Server 1 received: {data}")
            
            # Echo back to client
            await manager.send_personal_message(f"Echo: {data}", websocket)
            
            # Forward to Server 2 if connected
            await manager.send_to_server2(f"From Server 1: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/connect-server2")
async def connect_to_server2():
    """Endpoint to establish connection with Server 2"""
    success = await manager.connect_to_server2()
    return {"status": "connected" if success else "failed"}

@app.post("/send-to-server2")
async def send_to_server2(message: str):
    """Endpoint to send message to Server 2"""
    await manager.send_to_server2(message)
    return {"status": "sent"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
