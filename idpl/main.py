import sys
import time
import asyncio
import threading
import webbrowser
from dataclasses import dataclass, field

from nlp.pipeline import NLPPipeline
from stt.recorder import VADAudioRecorder
from stt.transcriber import WhisperTranscriber
from ble.client import BLEClient
from telemetry.mock import MockTelemetry
from server.ws_server import WebSocketServer
from server.http_server import HTTPServer

@dataclass
class SharedState:
    pitch: float = 0.0
    velocity: float = 0.0
    height: float = 150.0
    enc_left: int = 0
    enc_right: int = 0
    uptime: float = 0.0
    last_cmd: str = "NONE"
    last_intent: str = "NONE"
    last_confidence: float = 0.0
    last_raw_text: str = ""
    last_vel_extracted: float = 1.0
    last_height_extracted: float = 150.0
    ble_connected: bool = False
    voice_active: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)

def mock_telemetry_thread_func(state):
    mock = MockTelemetry(state)
    mock.run_forever()

def ws_thread_func(state, ble_client):
    server = WebSocketServer(state, ble_client)
    asyncio.run(server.serve())

def voice_thread_func(state, pipeline, recorder, transcriber, ble_client):
    while True:
        with state.lock:
            active = state.voice_active
        
        if not active:
            time.sleep(0.5)
            continue
            
        audio = recorder.record_utterance()
        if audio is not None:
            text = transcriber.transcribe(audio)
            if text:
                result = pipeline.infer(text)
                with state.lock:
                    state.last_raw_text = result["raw_text"]
                    state.last_intent = result["intent"]
                    state.last_confidence = result["confidence"]
                    state.last_vel_extracted = result["velocity"]
                    state.last_height_extracted = result["height"]
                    state.last_cmd = f"VOICE → {result['intent']}"
                
                print(f"[VOICE] \"{text}\" → {result['intent']} @ {result['velocity']} m/s (conf: {result['confidence']*100:.1f}%)")
                
                try:
                    asyncio.run(ble_client.send_command(result["ble_payload"]))
                except Exception as e:
                    print(f"[VOICE] Command send error: {e}")
            else:
                print("[VOICE] Could not transcribe audio.")

def uptime_updater(state):
    start_time = time.time()
    while True:
        with state.lock:
            state.uptime = time.time() - start_time
        time.sleep(1)

def main():
    print("[INIT] Loading NLP pipeline...")
    pipeline = NLPPipeline()
    pipeline.startup()

    state = SharedState()
    
    print("[BLE]  Starting BLE scan thread...")
    ble_client = BLEClient(state)
    t_ble = threading.Thread(target=lambda: asyncio.run(ble_client.run_forever()), daemon=True)
    t_ble.start()

    t_mock = threading.Thread(target=mock_telemetry_thread_func, args=(state,), daemon=True)
    t_mock.start()

    print("[STT]  Loading Whisper tiny.en model...")
    recorder = VADAudioRecorder()
    transcriber = WhisperTranscriber()
    print("[STT]  Whisper ready.")

    print("[WS]   WebSocket server starting on ws://localhost:8765")
    t_ws = threading.Thread(target=ws_thread_func, args=(state, ble_client), daemon=True)
    t_ws.start()

    t_voice = threading.Thread(target=voice_thread_func, args=(state, pipeline, recorder, transcriber, ble_client), daemon=True)
    t_voice.start()
    
    t_uptime = threading.Thread(target=uptime_updater, args=(state,), daemon=True)
    t_uptime.start()

    print("[HTTP] Dashboard at http://localhost:8000")
    http_server = HTTPServer()
    
    print("[MAIN] All systems nominal. Opening browser...")
    webbrowser.open('http://localhost:8000')

    try:
        http_server.run()
    except KeyboardInterrupt:
        print("\n[MAIN] Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
