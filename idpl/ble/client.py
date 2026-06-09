import json
import asyncio
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

TARGET_NAME = "Biped_Bot"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class BLEClient:
    def __init__(self, shared_state):
        self.client = None
        self.connected = False
        self.state = shared_state

    async def scan_and_connect(self) -> bool:
        print(f"[BLE] Scanning for {TARGET_NAME}...")
        try:
            device = await BleakScanner.find_device_by_name(TARGET_NAME, timeout=10.0)
        except Exception as e:
            print(f"[BLE] Scanner error: {e}")
            return False
        
        if not device:
            print("[BLE] Device not found, retry in 5s")
            return False
            
        try:
            self.client = BleakClient(device)
            await self.client.connect()
            self.connected = True
            with self.state.lock:
                self.state.ble_connected = True
            print("[BLE] Connected!")
            return True
        except BleakError as e:
            print(f"[BLE] Connect error: {e}")
            return False

    async def send_command(self, payload: str) -> bool:
        if not self.connected or not self.client:
            return False
            
        try:
            await self.client.write_gatt_char(CHAR_UUID, payload.encode())
            return True
        except BleakError:
            self.connected = False
            with self.state.lock:
                self.state.ble_connected = False
            return False

    async def telemetry_notify_handler(self, sender, data: bytearray):
        try:
            telemetry = json.loads(data.decode())
            with self.state.lock:
                if "pitch" in telemetry: self.state.pitch = telemetry["pitch"]
                if "velocity" in telemetry: self.state.velocity = telemetry["velocity"]
                if "height" in telemetry: self.state.height = telemetry["height"]
                if "enc_left" in telemetry: self.state.enc_left = telemetry["enc_left"]
                if "enc_right" in telemetry: self.state.enc_right = telemetry["enc_right"]
        except json.JSONDecodeError:
            pass

    async def enable_telemetry_notify(self):
        if self.connected and self.client:
            try:
                await self.client.start_notify(CHAR_UUID, self.telemetry_notify_handler)
                print("[BLE] Telemetry notifications enabled")
            except BleakError as e:
                print(f"[BLE] Notify error: {e}")

    async def run_forever(self):
        while True:
            if not self.connected:
                success = await self.scan_and_connect()
                if success:
                    await self.enable_telemetry_notify()
                else:
                    await asyncio.sleep(5)
            else:
                if not self.client.is_connected:
                    print("[BLE] Disconnected")
                    self.connected = False
                    with self.state.lock:
                        self.state.ble_connected = False
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1)
