import re

class NLPPipeline:
    def __init__(self):
        self._patterns = [
            (re.compile(r"\b(stop|halt|pause|stand still|freeze)\b", re.I), "STOP"),
            (re.compile(r"\b(left|turn left|rotate left|spin left)\b", re.I), "TURN_LEFT"),
            (re.compile(r"\b(right|turn right|rotate right|spin right)\b", re.I), "TURN_RIGHT"),
            (re.compile(r"\b(back|backward|reverse|reverse\b)\b", re.I), "DRIVE_BACKWARD"),
            (re.compile(r"\b(forward|ahead|go straight|move forward)\b", re.I), "DRIVE_FORWARD"),
            (re.compile(r"\b(speed|fast|slow|velocity)\b", re.I), None),
        ]

    def startup(self):
        return None

    def infer(self, text: str):
        raw_text = text.strip() if isinstance(text, str) else ""
        lowered = raw_text.lower()
        command = None
        velocity = 0.5
        height = 150.0
        confidence = 0.65

        for pattern, intent in self._patterns:
            if pattern.search(raw_text):
                if intent is not None:
                    command = intent
                    confidence = 0.92
                    break

        if command is None:
            command = "DRIVE_FORWARD" if lowered else "STOP"
            confidence = 0.55 if lowered else 0.0

        speed_match = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*(m/s|meters per second|mps|meters)\b", lowered)
        if speed_match:
            try:
                velocity = max(0.1, min(1.0, float(speed_match.group(1))))
            except ValueError:
                velocity = 0.5

        height_match = re.search(r"\b([0-9]{2,3})\s*(mm|millimeters|millimetres)\b", lowered)
        if height_match:
            try:
                height = float(height_match.group(1))
            except ValueError:
                height = 150.0

        if command == "DRIVE_FORWARD" and velocity == 0.5:
            velocity = 0.5
        if command == "DRIVE_BACKWARD" and velocity == 0.5:
            velocity = 0.5

        ble_payload = {
            "cmd": command,
            "val": velocity,
            "height": height,
        }

        return {
            "raw_text": raw_text,
            "intent": command,
            "confidence": confidence,
            "velocity": velocity,
            "height": height,
            "ble_payload": ble_payload,
        }
