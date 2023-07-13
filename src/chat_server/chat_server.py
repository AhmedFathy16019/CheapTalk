import argparse
from .chat_controller import ChatController
from .chat_publisher import ChatPublisher
from .chat_subscriber import ChatSubscriber
from .exceptions_custom import ClientError, validate_nickname
import logging
import selectors
import socket
from typing import Dict


logger = logging.getLogger("CheapTalk")

BUFFER_SIZE = 1024
ENCODING = 'UTF-8'

class ChatServer:

    def __init__(self, address: tuple):
        self.server_address = address
        self.ctrl_listener = None
        # self.controllers: Dict[socket.socket, ChatController]
        self.controllers = {}
        self.publisher = ChatPublisher()
        self.selector = selectors.DefaultSelector()
    
    def onhello_controller(self, controller: ChatController, nickname: str) -> socket.socket:
        try:
            if nickname in self.publisher.subscribers:
                raise ClientError("INVALID NICKNAME: Nickname is already taken, try another one")
            else:
                try:
                    validate_nickname(nickname) 
                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # Allow the reuse of the local socket address, even if the socket is in a TIME_WAIT state
                    new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    # Dynamically bind the port
                    new_socket.bind(('', 0))
                    new_socket.listen()
                    self.ctrl_listener.setblocking(False)
                    self.selector.register(new_socket, selectors.EVENT_READ, data=['Data_Listener', self.establish_data])
                    return new_socket
                except OSError as err: 
                    logger.error(err)
                    controller.on_close(controller)
        except ClientError as err:
            logger.error(err)
            controller.on_close()


    def onclose_controller(self, controller: ChatController):
        if controller.peer_socket:
            self.selector.unregister(controller.peer_socket)
        if controller.data_listener:
            self.selector.unregister(controller.data_listener)
        del self.controllers[controller.peer_socket]
        controller.close()
        ret_sub = self.publisher.remove_subscriber(controller.nickname)
        if ret_sub:
            ret_sub.close()


    def onclose_subscriber(self, subscriber: ChatSubscriber):
        self.publisher.remove_subscriber(subscriber)
        subscriber.close()
    
    def accept_connection(self, socket:socket.socket):
        control_socket, address = socket.accept()
        control_socket.setblocking(False)
        new_controller = ChatController(None, address, control_socket, None, self.publisher, self.onhello_controller, self.onclose_controller)
        self.selector.register(control_socket, selectors.EVENT_READ, data=["Controller"])
        self.controllers[control_socket] = new_controller


    def establish_data(self, data_listener: socket.socket):
        data_channel, data_address = data_listener.accept()
        for controller_socket, controller in self.controllers.items():
            if controller.data_listener == data_listener:
                new_subscriber = ChatSubscriber(controller.nickname, data_address, data_channel, self.onclose_subscriber)
                subscriber_ret = self.publisher.put_subscriber(new_subscriber)
                if subscriber_ret:
                    subscriber_ret.close()



    def run(self):
        self.ctrl_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ctrl_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ctrl_listener.bind(self.server_address)
        self.ctrl_listener.listen()
        self.ctrl_listener.setblocking(False)
        self.selector.register(self.ctrl_listener, selectors.EVENT_READ, data=['Controller_Listener', self.accept_connection])
        
        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data[0]=='Controller_Listener':
                    key.data[1](key.fileobj)
                elif key.data[0]=='Data_Listener':
                    key.data[1](key.fileobj)
                elif key.data[0]=='Controller':
                    try:
                        self.controllers[key.fileobj].handle_input()
                    except OSError as err:
                        logger.error(f"OSError: {err}")
                        self.controllers[key.fileobj].on_close(self, self.controllers[key.fileobj])        
                        self.selector.close()





