#add imports
from .chat_subscriber import ChatSubscriber
from .chat_message import ChatMessage
from .chat_channel import ChatChannel
from .exceptions_custom import ClientError
from typing import Dict

DEFAULT_CHANNEL = "lobby"

class ChatPublisher:
    def __init__(self):
        self.subscribers: Dict[str, ChatSubscriber] = {}
        self.channels: Dict[str, ChatChannel] = {}
        self.channels["lobby"] = ChatChannel("lobby")

    def put_subscriber(self, subscriber: ChatSubscriber) -> ChatSubscriber:
        # Check if there is already a subscriber for the client
        if subscriber.nickname in self.subscribers:
            # retain the old the subscriber and replace it with the new subscriber
            old_subscriber = self.subscribers[subscriber.nickname]
            self.remove_subscriber(subscriber.nickname)
            self.subscribers[subscriber.nickname] = subscriber
            self.channels["lobby"].put_subscriber(subscriber)
            # return the old subscriber to the server
            return old_subscriber
        else:
            # Add the subscriber to the lobby
            self.subscribers[subscriber.nickname] = subscriber
            self.channels["lobby"].put_subscriber(subscriber)
            return None
        

    def remove_subscriber(self, subscriber_name: str) -> ChatSubscriber:
        # Remove the subsrciber from the lobby and retain it
        subscriber = self.subscribers.pop(subscriber_name, None)
        # Check if there is no subscriber with the given nickname and raise a client error
        if subscriber is None:
            raise ClientError(f"No subscriber with name '{subscriber_name}' found.")
        # Iterate over all channels to remove the subscriber from all channels including the lobby
        for channel_nickname, channel in self.channels.items():
            if subscriber in channel.subscribers:
                channel.remove_subscriber(subscriber)
        return subscriber
        

    def send_message(self, message: ChatMessage):
        # If the destination is a channel
        if message.destination[0] == '#':
            # Check if there is a channel with the nickname given through the publisher
            
            if not message.destination[1:] in self.channels.keys():
                raise ClientError(f"Channel {message.destination[1:]} does not exist")
            # Call the send_message method of the desired channel
            self.channels[message.destination[1:]].send_message(message)
            #self.subscribers[message.sender]._send(f"OK message sent to {message.destination}\r\n")
            #self.subscribers[message.sender]._send(f"OK message sent to {message.destination}\r\n")
        # If the destination is a subscriber
        elif message.destination[0] == '@':
            # Check if a subscriber exists with the given nickname
            if not message.destination[1:] in self.subscribers.keys():
                raise ClientError(f"Subscriber {message.destination[1:]} does not exist")
            # Call the send_message method of the desired subscriber
            self.subscribers[message.destination[1:]].send_message(message)
            self.subscribers[message.sender]._send(f"OK message sent to {message.destination}\r\n")