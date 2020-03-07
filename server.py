import traceback
from socket import *
from ipaddress import ip_address
import re
import sys

clients = {}

HOST = ''
PORT = int(sys.argv[1])
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDR)

http = "HTTP/1.1 "
r200 = "200 OK\n"
r400 = "400 Bad Request\n"
r404 = "404 Not Found\n"
r405 = "405 Method Not Allowed\n"
r500 = "500 Internal Server Error\n"


def accept_incoming_connections():
    """Sets up handling for incoming connections"""
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
                        response = url_name + ":" + url_type + "=" + ipaddr_list[0] + "\n"
                        result = header + "\n" + response
                    except OSError:
                        result = r404

                elif url_type == "PTR":
                    try:
                        ip_address(url_name)  # check if IP format is valid
                        try:
                            hostname, _, _ = gethostbyaddr(url_name)
                            header = http + r200
                            response = url_name + ":" + url_type + "=" + hostname + "\n"
                            result = header + "\n" + response
                        except OSError:
                            traceback.print_tb()
                            result = r404
                    except ValueError:
                        result = r400

            client.send(bytes(result, "utf8"))


        elif request == "POST":
            result = r400
            if (re.match(r"^POST /dns-query HTTP/1.1", msg)) is None:
                client.send(bytes(http + result, "utf8"))
            else:
                tmp_msg = msg.split("\n")[7:]
                msg = []
                for line in tmp_msg:
                    # if the line is fill with whitespaces and/or newline, pop this from list
                    if re.match(r"^.*\w+.*$", line) is not None:
                        msg.append(line)
                    else:
                        result = 400400
                        break
                if result == 400400:
                    client.send(bytes(http + r400, "utf8"))
                else:
                    result_list = []
                    for query in msg:
                        request_args = re.match(r"^(\S*)(?:\s*):(?:\s*)(\w*)", query)
                        if request_args is None:
                            continue
                        url_name = request_args.group(1)
                        url_type = request_args.group(2)
                        if url_type == "A":

                            print("\n___", getaddrinfo(url_name, port=80), "___")

                            if re.match(r"^\w*\.(\w(-\w)?\.)*\w+$", url_name):
                                _, _, ipaddr_list = gethostbyname_ex(url_name)
                                response = url_name + ":" + url_type + "=" + ipaddr_list[0] + "\n"
                                result_list.append(response)
                                print("A\n")
                            else:

                                continue
                        elif url_type == "PTR":
                            try:
                                ip_address(url_name)
                                hostname, _, _ = gethostbyaddr(url_name)
                                response = url_name + ":" + url_type + "=" + hostname + "\n"
                                result_list.append(response)
                                print("PTR\n")
                            except ValueError:
                                continue
                        else:
                            continue
                    if len(result_list) != 0:
                        client.send(bytes(http + r200 + "\n", "utf8"))
                        print("\n...", result_list)
                        for result in result_list:
                            client.send(bytes(result, "utf8"))
                    else:
                        client.send(bytes(http + r400, "utf8"))
        else:
            client.send(bytes(http + r405, "utf8"))

        client.close()


if __name__ == "__main__":
    SERVER.listen(1)  # Listen for 1 connections at max.
    print("Waiting for connection...")
    accept_incoming_connections()
    SERVER.close()

"curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A"


# getnameinfo()
# inet_aton()


r"^\w*\.(\w(\-\w)?\.)*\w+$"
