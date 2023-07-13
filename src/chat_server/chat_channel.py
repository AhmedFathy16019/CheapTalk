from .chat_subscriber import ChatSubscriber
from .chat_message import ChatMessage
from .exceptions_custom import ClientError
from typing import Set


class ChatChannel:

    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.subscribers: Set[ChatSubscriber] = set()


    def put_subscriber(self, subscriber: ChatSubscriber):
        self.subscribers.add(subscriber)


    # Does not make much sense, needs more revision
    def replace_subscriber(self, subscriber: ChatSubscriber):
        self.subscribers.remove(subscriber)
        self.subscribers.add(subscriber)


    def remove_subscriber(self, subscriber: ChatSubscriber):
        self.subscribers.remove(subscriber)


    def send_message(self, message: ChatMessage):
        for sub in self.subscribers:
            if message.sender == sub.nickname:
                for subscriber in self.subscribers:
                    subscriber.send_message(message)
                return
        raise ClientError(f"Sender {message.sender} is not subscribed to the channel {self.channel_name}, use the command JOIN first")
