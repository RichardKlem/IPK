from socket import gethostbyname_ex, gethostbyaddr, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
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
    while True:
        client, client_address = SERVER.accept()
        msg = client.recv(BUFSIZ).decode("utf8")
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
                    # když nastane vyjimka, nejedna se o IP a můžeme zkusit najit IP podle jmena
                    try:
                        ip_address(url_name)
                    except ValueError:
                        try:
                            _, _, ipaddr_list = gethostbyname_ex(url_name)
                            header = http + r200
                            response = url_name + ":" + url_type + "=" + ipaddr_list[0] + "\n"
                            result = header + "\n" + response
                        except OSError:
                            result = r404

                elif url_type == "PTR":
                    try:
                        ip_address(url_name)
                        try:
                            hostname, _, _ = gethostbyaddr(url_name)
                            header = http + r200
                            response = url_name + ":" + url_type + "=" + hostname + "\n"
                            result = header + "\n" + response
                        except OSError:
                            result = r404
                    except ValueError:
                        result = r400

            client.send(bytes(result + "\n", "utf8"))

        elif request == "POST":
            result = r400
            if (re.match(r"^POST /dns-query HTTP/1.1", msg)) is None:
                client.send(bytes(http + result, "utf8"))
            else:
                tmp_msg = msg.split("\n")[7:]
                if tmp_msg[len(tmp_msg)-1] == "":
                    tmp_msg.pop()
                msg = []
                resultos = 0
                for line in tmp_msg:
                    res = re.match(r"^\s*\S+.*$", line)
                    if res is not None:
                        msg.append(line)
                    else:
                        resultos = 400400
                        break

                error_list = []
                if resultos == 400400:
                    error_list.append(r400)
                else:
                    result_list = []
                    for query in msg:
                        request_args = re.match(r"^(\S*)(?:\s*):(?:\s*)(\w*)$", query)
                        if request_args is None:
                            continue
                        url_name = request_args.group(1)
                        url_type = request_args.group(2)
                        if url_type == "A":
                            # když nastane vyjimka, nejedna se o IP a můžeme zkusit najit IP podle jmena
                            try:
                                ip_address(url_name)
                            except ValueError:
                                try:
                                    _, _, ipaddr_list = gethostbyname_ex(url_name)
                                    response = url_name + ":" + url_type + "=" + ipaddr_list[0] + "\n"
                                    result_list.append(response)
                                except OSError:
                                    error_list.append(r404)
                                    continue
                        elif url_type == "PTR":
                            try:
                                ip_address(url_name)  # check if IP format is valid
                                try:
                                    hostname, _, _ = gethostbyaddr(url_name)
                                    response = url_name + ":" + url_type + "=" + hostname + "\n"
                                    result_list.append(response)
                                except OSError:
                                    error_list.append(r404)
                            except ValueError:
                                error_list.append(r400)
                                continue
                        else:
                            error_list.append(r400)
                            continue

                    if len(result_list) != 0:
                        client.send(bytes(http + r200 + "\n", "utf8"))
                        for answer in result_list:
                            client.send(bytes(answer, "utf8"))
                    else:
                        if r400 in error_list:
                            client.send(bytes(http + r400 + "\n", "utf8"))
                        elif r404 in error_list:
                            client.send(bytes(http + r404 + "\n", "utf8"))
                        else:
                            client.send(bytes(http + r500 + "\n", "utf8"))
        else:
            client.send(bytes(http + r405 + "\n", "utf8"))

        client.close()


if __name__ == "__main__":
    SERVER.listen(1)  # Listen for 1 connection
    try:
        accept_incoming_connections()
    except KeyboardInterrupt:
        sys.exit()
    SERVER.close()
