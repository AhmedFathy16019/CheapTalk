from .chat_message import ChatMessage
import json
import logging
import socket
from typing import Callable


ENCODING = 'UTF-8'
logger = logging.getLogger("CheapTalk")

class ChatSubscriber:

    def __init__(self, nickname: str, peer_address: tuple, peer_socket: socket.socket, on_close: Callable[['ChatSubscriber'], None]):
        self.nickname = nickname
        self.peer_address = peer_address
        self.peer_socket = peer_socket
        self.on_close = on_close


    def _send(self, message: str):
        # Check to catch socket exceptions for sending
        try:
            self.peer_socket.send(message.encode(ENCODING))
        except socket.error as err:
            # log error and notify server to close the subscriber's data channel
            logger.error(f"Socket error occurred for {self.nickname}: {err}")
            # Invoke the on_close method for clean up
            self.on_close(self)


    # send message to peer_socket
    def send_message(self, message: ChatMessage):
        message_to_send = "MESSAGE " + message.to_json()
        self._send(message_to_send)


    # send subscribe message to client
    def send_subscribe(self, channel_name: str, nickname: str):
        subscribe_message = f"SUBSCRIBE {channel_name} {nickname}\r\n"
        self._send(subscribe_message)


     # send unsubscribe message to client
    def send_unsubscribe(self, channel_name: str, nickname: str):
        unsubscribe_message = f"UNSUBSCRIBE {channel_name} {nickname}\r\n"
        self._send(unsubscribe_message)


    def close(self):
        # self.peer_socket.shutdown()
        self.peer_socket.close()
