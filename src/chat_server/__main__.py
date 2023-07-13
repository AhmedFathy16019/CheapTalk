from .chat_server import ChatServer
import logging
import argparse
import sys


SERVER_IP = "0.0.0.0"
SERVER_PORT = 10005

def parse():
    parser = argparse.ArgumentParser(description="A continuous client for sending commands to CheapTalk")
    parser.add_argument('-p', '--port', type=int, default=SERVER_PORT, help="port to connect to")
    parser.add_argument("host", type=str, default=SERVER_IP, help="IP address for the server host")
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    args = parse()
    address = (args.host, args.port)
    serv = ChatServer(address)
    serv.run()