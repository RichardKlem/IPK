from time import sleep
from socket import *
from ipaddress import ip_address
import re
from socketserver import TCPServer
clients = {}

HOST = ''
PORT = 5353
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDR)

http = "HTTP/1.1"
r200 = "200 OK\n"
r400 = "400 Bad Request\n"
r404 = "404 Not Found\n"
r500 = "500 Internal Server Error\n"



def accept_incoming_connections():
    """Sets up handling for incoming clients"""
    while True:
        client, client_address = SERVER.accept()
        msg = client.recv(BUFSIZ).decode("utf8")
        print(msg)
        request = re.match(r"^(GET|POST)", msg).group(1)

        if request == "GET":
            msg = msg.split("\n")[0]
            request_args = re.match(r"^GET /resolve\?name=(.*)&type=(.*) HTTP/1\.1", msg)
            result = r400
            if len(request_args.groups()) != 2:
                pass
            else:
                url_name = request_args.group(1)
                url_type = request_args.group(2)
                result = r400
                if url_type == "A":
                    try:
                        _, _, ipaddr_list = gethostbyname_ex(url_name)
                        header = http + r200
                        result = header + "\n" + url_name + ":" + url_type + "=" + ipaddr_list[0] + "\n"
                    except OSError:
                        result = r404

                elif url_type == "PTR":
                    try:
                        ip_address(url_name)  # check if IP format is valid
                        try:
                            hostname, _, _ = gethostbyaddr(url_name)
                            result = "HTTP/1.1 200 OK\n" + url_name + ":" + url_type + "=" + hostname + "\n"
                        except OSError:
                            result = r404
                    except ValueError:
                        result = r400

            client.send(bytes(result, "utf8"))

        elif request == "POST":
            result = r400
            if (re.match(r"^POST /dns-query HTTP/1.1", msg)) is None:
                client.send(bytes(result, "utf8"))
            else:
                msg = msg.split("\n")[7:]

                for query in msg:
                    request_args = re.match(r"^(.*):(.*)", query)
                    url_name = request_args.group(1)
                    url_type = request_args.group(2)
                    if url_type == "A":
                        _, _, ipaddr_list = gethostbyname_ex(url_name)
                        result = "200 OK " + url_name + ":" + url_type + "=" + ipaddr_list[
                            0] + "\n"
                    elif url_type == "PTR":
                        try:
                            ip_address(url_name)
                            hostname, _, _ = gethostbyaddr(url_name)
                            result = "200 OK " + url_name + ":" + url_type + "=" + hostname + "\n"
                        except ValueError:
                            result = "500 Internal Server Errorn\n"
                            # result = "400 Bad Request"
                    client.send(bytes(result, "utf8"))
        else:
            exit("405 Method Not Allowed\n")

        client.close()
        # hostname, aliases, ipaddr_list = gethostbyname_ex(url_name)
        # print(url_method, url_name, url_type)
        # hostname, aliases, ipaddr_list = gethostbyname_ex(url_name)
        # ipaddr = socket.gethostbyaddr(ipaddr_list[0])

        # print(hostname, aliases, ipaddr_list)


if __name__ == "__main__":
    SERVER.listen(1)  # Listen for 1 connections at max.
    print("Waiting for connection...")
    accept_incoming_connections()
    SERVER.close()

"curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A"


# getnameinfo()
# inet_aton()


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
            broadcast(msg, name + ": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """broadcast a message to all the clients."""
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)
