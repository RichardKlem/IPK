#!/usr/bin/env python3

from socket import *
import re

clients = {}
addresses = {}

HOST = ''
PORT = 5353
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDR)


def accept_incoming_connections():
    """Sets up handling for incoming clients"""
    while True:
        client, client_address = SERVER.accept()
        msg = client.recv(BUFSIZ).decode("utf8")
        msg_list = msg.split("\n")
        msg = msg_list[0]
        #client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
        request = re.match(r"(GET|POST) /resolve\?name=(.*)&type=(.*) HTTP/1.1", msg)
        url_method = request.group(1)
        url_name = request.group(2)
        url_type = request.group(3)
        print(url_method, url_name, url_type)
        """
        if not :
            exit("405 Method Not Allowed")
        elif request_type == 'GET':

        else:"""

        if msg != bytes("{GET /resolve?name=apple.com&type=A HTTP/1.1}", "utf8"):
            print("Eeeooooo")
            exit(0)
        exit(0)
        hostname, aliases, ipaddr_list = gethostbyname_ex(
                "www.fit.vutbr.cz")
        # ipaddr = socket.gethostbyaddr(ipaddr_list[0])

        print(hostname, aliases, ipaddr_list)


def handle_client(client):  # takes socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    client[client] = name

    while True:
        msg = client.recv(BUFSIZ)

        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """broadcast a message to all the clients."""
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)


if __name__ == "__main__":
    SERVER.listen(1)  # Listen for 1 connections at max.
    print("Waiting for connection...")
    accept_incoming_connections()
    SERVER.close()


"curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A"