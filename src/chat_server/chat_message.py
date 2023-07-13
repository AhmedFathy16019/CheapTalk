from datetime import datetime

class ChatMessage:
    def __init__(self, timestamp: datetime, sender: str, destination: str, text: str):
        self.timestamp = timestamp
        self.sender = sender
        self.destination = destination
        self.text = text

    def to_json(self):
        return f"{self.timestamp} {self.sender} {self.destination} {self.text}\r\n"
