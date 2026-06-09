import json
import asyncio
import websockets

class WebSocketServer:
    def __init__(self, shared_state, ble_client, host="localhost", port=8765):
        self.state = shared_state
        self.ble_client = ble_client
        self.host = host
        self.port = port
        self.clients = set()

    async def send_loop(self, websocket):
        try:
            while True:
                with self.state.lock:
                    data = {
                        "pitch": self.state.pitch,
                        "velocity": self.state.velocity,
                        "height": self.state.height,
                        "enc_left": self.state.enc_left,
                        "enc_right": self.state.enc_right,
                        "uptime": self.state.uptime,
                        "last_cmd": self.state.last_cmd,
                        "last_intent": self.state.last_intent,
                        "last_confidence": self.state.last_confidence,
                        "last_raw_text": self.state.last_raw_text,
                        "last_vel_extracted": self.state.last_vel_extracted,
                        "last_height_extracted": self.state.last_height_extracted,
                        "ble_connected": self.state.ble_connected,
                        "voice_active": self.state.voice_active
                    }
                await websocket.send(json.dumps(data))
                await asyncio.sleep(0.1)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def recv_loop(self, websocket):
        try:
            async for message in websocket:
                data = json.loads(message)
                if "cmd" in data:
                    cmd = data["cmd"]
                    if cmd == "VOICE_TOGGLE":
                        with self.state.lock:
                            self.state.voice_active = not self.state.voice_active
                    else:
                        with self.state.lock:
                            self.state.last_cmd = f"MANUAL → {cmd}"
                            self.state.last_intent = cmd
                            if "val" in data:
                                self.state.last_vel_extracted = float(data["val"])
                            if "height" in data:
                                self.state.last_height_extracted = float(data["height"])
                        
                        await self.ble_client.send_command(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except json.JSONDecodeError:
            pass

    async def handler(self, websocket):
        self.clients.add(websocket)
        send_task = asyncio.create_task(self.send_loop(websocket))
        recv_task = asyncio.create_task(self.recv_loop(websocket))
        
        done, pending = await asyncio.wait(
            [send_task, recv_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        
        for task in pending:
            task.cancel()
            
        self.clients.remove(websocket)

    async def serve(self):
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever
