# HTTP Handler
# By David van Erkelens
# Studentnr 10264019
# Department of Computer Science
# University of Amsterdam
# 12 november 2012

import socket
import os

def process_request(conn):
    data = conn.recv(1024)
    print "Requesting "
    print data
    request = data.split(" ")
    if(request[0] != "GET"):
        conn.send("""HTTP/1.1 501 Not Implemented\r\n""")
    else:
        req_file = request[1][1:]
        if(os.path.exists(req_file)):
            file = open(req_file, 'r')
            data = file.read()
            conn.send("""HTTP/1.1 200 OK\r\n""" + data)
        else:
            conn.send("""HTTP/1.1 404 Not Found\r\n""")

def main():
    serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_socket.bind(("localhost", 1337))
    serv_socket.listen(1)
    while 1:
        connection, address = serv_socket.accept()
        process_request(connection)
    server_socket.close()

if __name__ == "__main__":
    main()
