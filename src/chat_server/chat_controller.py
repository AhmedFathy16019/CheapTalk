from .chat_publisher import ChatPublisher
from .chat_channel import ChatChannel
from .chat_message import ChatMessage
from .chat_subscriber import ChatSubscriber
from datetime import datetime
from .exceptions_custom import ClientError, validate_channel, validate_nickname
import logging
import socket
from typing import Callable


ENCODING = 'UTF-8'
logger = logging.getLogger("CheapTalk")


def command_hello(controller: 'ChatController', args):
    try:
        # Check if args is a list
        if len(args)>1:
            raise ClientError("INVALID ARGUMENTS: command HELLO expects only {{nickname}} argument")
        # Invoke the on_hello method
        controller.data_listener = controller.on_hello(controller, args[0])
        _, data_port = controller.data_listener.getsockname()
        logger.debug(f"grapped data socket with port: {data_port}")
        controller.nickname = args[0]
        controller.peer_socket.send(f"OK {data_port}\r\n".encode(ENCODING))
    except ClientError as err: 
        logger.error(err)
        controller.peer_socket.send(f"ERROR {err}\r\n".encode(ENCODING))
        controller.on_close(controller)


def command_bye(controller:'ChatController', args):
    try: 
        if args:
            ClientError("BYE command does not expect any arguments")
        controller.peer_socket.send("OK\r\n".encode(ENCODING))
        controller.on_close(controller)
    except ClientError as err:
        logger.error(err)
        controller.on_close(controller)


def command_send(controller: 'ChatController', args: list):
    # Check and catch client errors
    try:
        # If there are insufficient arguments
        if len(args)<2:
            raise ClientError("INVALID ARGUMENTS: command SEND expects arguments {{Destination}} and {{Text}}")
        if args[0][0] == '#':
            validate_channel(args[0][1:])
        elif args[0][0] == '@':
            validate_nickname(args[0][1:])
        else:
            raise ClientError("INVALID DESTINATION: {{Destination}} argument must start with a '#' for channels or a '@' for subscribers")
        # Create a ChatMessage object and call for the publisher send_message method
        message = ChatMessage(datetime.now().astimezone().isoformat(), controller.nickname, args[0], args[1])
        controller.publisher.send_message(message)
        controller.peer_socket.send(f"OK message sent to {message.destination}\r\n".encode(ENCODING))
    except ClientError as err:
        # Log the client error and call for on_close method for cleanup
        logger.error(err)
        controller.on_close(controller)


def command_join(controller: 'ChatController', args):
    try:
        # Check if the recieved arguments is an empty list
        if not args:
            raise ClientError("INVALID ARGUMENTS: command JOIN expects argument {{Channel}}")
        # Check if the recieved arguments is more than one or not
        if isinstance(args, list) and len(args)>1:
            raise ClientError("INVALID ARGUMENT: command JOIN expects argument {{Channel}} only")
        # Check if the channel exists with the nickname given
        if args[0] in controller.publisher.channels:
            controller.publisher.channels[args[0]].put_subscriber(controller.publisher.subscribers[controller.nickname])
            controller.peer_socket.send(f"OK joined channel {args[0]}\r\n".encode(ENCODING))
        else:
            # Validate the syntax of the nickname
            validate_channel(args[0])
            # Create the channel and add it to the publisher
            new_channel = ChatChannel(args[0])
            controller.publisher.channels[args[0]] = new_channel
            # Put the subscriber in new channel
            controller.publisher.channels[args[0]].put_subscriber(controller.publisher.subscribers[controller.nickname])
            controller.peer_socket.send(f"OK joined channel {args[0]}\r\n".encode(ENCODING))
    except ClientError as err:
        logger.error(err)
        controller.on_close(controller)


def command_leave(controller: 'ChatController', args):
    try:
        if not args:
            raise ClientError("INVALID ARGUMENTS: command LEAVE expects argument {{Channel}}")
        if isinstance(args, list) and len(args)>1:
            raise ClientError("INVALID ARGUMENT: command LEAVE expects argument {{Channel}} only")
        if args[0] in controller.publisher.channels:
            controller.publisher.channels[args[0]].remove_subscriber(controller.publisher.subscribers[controller.nickname])
        else:
            raise ClientError(f"Channel {args[0]} doest not exist")  
        controller.peer_socket.send(f"OK left channel {args[0]}\r\n".encode(ENCODING))       
    except ClientError as err:
        logger.error(err)
        controller.on_close(controller)


def command_channels(controller: 'ChatController'):
    response = f"OK {len(controller.publisher.channels)}"
    for channel_name, channel in controller.publisher.channels.items():
        response += f"\n {channel_name}"   
    response+="\r\n"
    controller.peer_socket.send(response.encode(ENCODING))


def command_roster(controller: 'ChatController', channel:str):
    response = f"OK {len(controller.publisher.channels[channel[0][1:]].subscribers)}"
    for sub_name, sub in controller.publisher.subscribers.items():
        response += f"\n {sub_name}"
    response+="\r\n"
    controller.peer_socket.send(response.encode(ENCODING))


class ChatController:
    def __init__(self,
                 nickname: str,
                 peer_address: tuple,
                 peer_socket: socket.socket, #Event_Read socket
                 data_listener: socket.socket,
                 publisher: ChatPublisher,
                 on_hello: Callable[['ChatController', str], socket.socket],
                 on_close: Callable[['ChatController'], None]):
        self.nickname = nickname
        self.peer_address = peer_address
        self.peer_socket = peer_socket
        self.data_listener = data_listener
        self.publisher = publisher
        self.on_hello = on_hello
        self.on_close = on_close
        

    def handle_input(self):
        try:
            data = self.peer_socket.recv(1024).decode().strip()
            if not data:
                self.on_close(self)
            command, *args = data.split()
            if command == "HELLO":
                command_hello(self, args)
            elif command == "BYE":
                command_bye(self, args)
            elif command == "SEND":
                command_send(self, args)                
            elif command == "JOIN":
                command_join(self, args)
            elif command == "LEAVE":
                command_leave(self, args)
            elif command == "CHANNELS":
                command_channels(self)
            elif command == "ROSTER":
                command_roster(self, args)
        except OSError as err:
            logger.error(err)
            self.on_close(self)


    def close(self):
        # self.peer_socket.shutdown()
        self.peer_socket.close()
        # self.data_listener.shutdown()
        self.data_listener.close()
