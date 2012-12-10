# Netwerken en Systeembeveiliging
# Lab 8 - Distributed Sensor Network
# Author(s) and student ID(s):
# David van Erkelens and Jelte Fennema
# 10264019 and
# Group:
# Date: 7 december 2012
import sys
import struct
import time
import random
import math
from gui import MainWindow
from sensor import *
from socket import *



def socket_subscribe_mcast(sock, ip):
    """
    Subscribes a socket to multicast.
    """
    mreq = struct.pack("4sl", inet_aton(ip), INADDR_ANY)
    sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)



def main(argv):
    """
    Program entry point.
    """
    ## Create the multicast listener socket and suscribe to multicast.
    mcast = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    socket_subscribe_mcast(mcast, MCAST_GRP)
    # Set socket as reusable.
    mcast.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # Bind it to the multicast address.
    # NOTE: You may have to bind to localhost or '' instead of MCAST_GRP
    # depending on your operating system.
    # ALSO: In the lab room change the port to MCAST_PORT + group number
    # so that messages from different groups do not interfere.
    # When you hand in your code in it must listen on (MCAST_GRP, MCAST_PORT).
    mcast.bind((MCAST_GRP, MCAST_PORT))
    mcast.setblocking(0)

    ## Create the peer-to-peer socket.
    peer = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    # Set the socket multicast TTL so it can send multicast messages.
    peer.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 2)
    # Bind the socket to a random port.
    peer.bind(('', INADDR_ANY))
    ## This is the event loop.
    global window
    window = MainWindow()
    start = time.time()
    window.writeln("Starting at " + str(start))
    global x
    x = random.randrange(0, GRID_SIZE)
    global y
    y = random.randrange(0, GRID_SIZE)
    window.writeln("Position: " + str(x) + ":" + str(y))
    enc_msg = message_encode(MSG_PING, 0, (x, y), (0, 0))
    send_ping(mcast, enc_msg)
    window.writeln("Sending ping message...")
    while window.update():
        if(time.time() - start > PING_PERIOD):
            window.writeln("New ping! Time: " + str(time.time()))
            start = time.time()
            enc_msg = message_encode(MSG_PING, 0, (x, y), (0, 0))
            send_ping(mcast, enc_msg)
        try:
            message, address = mcast.recvfrom(2048)
            process_msg(message, address, mcast, peer)
        except:
            pass
        try:
            line = window.getline()
        except:
            pass
        if(line):
            window.writeln(line)

def send_ping(socket, message):
    socket.sendto(message, (MCAST_GRP, MCAST_PORT))

def send_pong(socket, message):
    socket.sendto(message, )

def process_msg(message, address, mcast, ucast):
    global x
    global y
    dec_msg = message_decode(message)
    global window
    if dec_msg[0] == MSG_PING:
        dec_x, dec_y = dec_msg[2]
        if dec_x == x and dec_y == y:
            window.writeln("received own ping")
            pass
        else:
            window.writeln("received other ping")
            dx = abs(dec_x - x)
            dx *= dx
            dy = abs(dec_y - y)
            dy *= dy
            if math.sqrt(dx + dy) > 50.0:
                window.writeln("in range, send pong")
                print "Send pong!"
            else:
                window.writeln("out of range, do nothing")


if __name__ == '__main__':
    sys.exit(main(sys.argv))
