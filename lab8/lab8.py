# Netwerken en Systeembeveiliging
# Lab 8 - Distributed Sensor Network
# Author(s) and student ID(s):
# David van Erkelens and Jelte Fennema
# Group: 5
# Date: 10 december 2012
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
    global mcast
    global peer
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
    peer.setblocking(0)
    ## This is the event loop.
    global window
    window = MainWindow()
    start = time.time()
    global x
    x = random.randrange(0, GRID_SIZE)
    global y
    y = random.randrange(0, GRID_SIZE)
    global nodes
    nodes = []
    global knownWaves
    knownWaves = []
    global father
    father = []
    global receivedEchoReps
    receivedEchoReps = []
    global recPayload
    recPayload = []
    global types
    types = []
    waves = 0
    window.writeln("Position: " + str(x) + ":" + str(y))
    enc_msg = message_encode(MSG_PING, 0, (x, y), (0, 0))
    peer.sendto(enc_msg, (MCAST_GRP, MCAST_PORT))
    while window.update():
        if(time.time() - start > PING_PERIOD):
            start = time.time()
            enc_msg = message_encode(MSG_PING, 0, (x, y), (0, 0))
            peer.sendto(enc_msg, (MCAST_GRP, MCAST_PORT))
            nodes = []
        try:
            message, address = mcast.recvfrom(2048)
            process_msg(message, address, peer, mcast)
        except:
            pass
        try:
            message, address = peer.recvfrom(2048)
            process_msg(message, address, peer, mcast)
        except:
            pass
        try:
            line = window.getline()
        except:
            pass
        if(line):
            if(line == "ping"):
                window.writeln("We'll be pinging now.")
                nodes = []
                start = time.time()
                enc_msg = message_encode(MSG_PING, 0, (x, y), (0, 0))
                peer.sendto(enc_msg, (MCAST_GRP, MCAST_PORT))
            elif(line == "list"):
                window.writeln("List of neighbors:")
                if(nodes == []):
                    window.writeln("No neighbors found.")
                else:
                    for n in nodes:
                        window.writeln(str(n[1]) + " @ " + str(n[0]))
            elif(line == "move"):
                x = random.randrange(0, GRID_SIZE)
                y = random.randrange(0, GRID_SIZE)
                window.writeln("New location of sensor: " + str(x) + ":" + str(y))
            elif(line == "echo"):
                if(nodes == []):
                    window.writeln("No neighbors, echo will be aborted.")
                else:
                    knownWaves.append((waves, (x, y)))
                    window.writeln("Added " + str((waves, (x, y))) + " to list of known waves")
                    for n in nodes:
                        echo = message_encode(MSG_ECHO, waves, (x, y), (x, y))
                        peer.sendto(echo, n[0])
                    waves += 1
                    receivedEchoReps.append(0)
                    father.append('dummy')
                    types.append(OP_NOOP)
                    recPayload.append(0)
            elif(line == "size"):
                if(nodes == []):
                    window.writeln("No neighbors, size will be aborted.")
                else:
                    knownWaves.append((waves, (x, y)))
                    window.writeln("Added " + str((waves, (x, y))) + " to list of known waves")
                    for n in nodes:
                        echo = message_encode(MSG_ECHO, waves, (x, y), (x, y), OP_SIZE)
                        peer.sendto(echo, n[0])
                    waves += 1
                    receivedEchoReps.append(0)
                    father.append('dummy')
                    recPayload.append(0)
                    types.append(OP_SIZE)
            else:
                window.writeln("This command is not supported")

def send_mcast(socket, message):
    socket.sendto(message, (MCAST_GRP, MCAST_PORT))

def send_ucast(socket, message, address):
    socket.sendto(message, address)

def process_msg(message, address, mcastt, ucast):
    global x
    global y
    global peer
    global mcast
    global nodes
    global knownWaves
    global father
    global recPayload
    global receivedEchoReps
    dec_msg = message_decode(message)
    global window
    if(dec_msg[0] == MSG_PING):
        dec_x, dec_y = dec_msg[2]
        if dec_x == x and dec_y == y:
            pass
        else:
            dx = abs(dec_x - x)
            dx *= dx
            dy = abs(dec_y - y)
            dy *= dy
            if math.sqrt(dx + dy) <= SENSOR_RANGE:
                enc_msg = message_encode(MSG_PONG, 0, (dec_x, dec_y), (x, y))
                peer.sendto(enc_msg, address)

    elif(dec_msg[0] == MSG_PONG):
        nodes.append((address, dec_msg[3]))

    elif(dec_msg[0] == MSG_ECHO):
        if(dec_msg[1], dec_msg[2]) in knownWaves:
            index = knownWaves.index((dec_msg[1], dec_msg[2]))
            rep = message_encode(MSG_ECHO_REPLY, dec_msg[1], dec_msg[2], (x, y))
            peer.sendto(rep, address)
        else:
            knownWaves.append((dec_msg[1], dec_msg[2]))
            index = knownWaves.index((dec_msg[1], dec_msg[2]))
            father.append(address)
            recPayload.append(0)
            types.append(dec_msg[4])
            if(len(nodes) == 1):
                if(dec_msg[4] == OP_SIZE):
                    rep = message_encode(MSG_ECHO_REPLY, dec_msg[1], dec_msg[2], (x, y), OP_SIZE, 1)
                else:
                    rep = message_encode(MSG_ECHO_REPLY, dec_msg[1], dec_msg[2], (x, y))
                peer.sendto(rep,  address)
            else:
                for n in nodes:
                    if(n[0] == father[index]):
                        pass
                    else:
                        if(dec_msg [4] == OP_SIZE):
                            echo = message_encode(MSG_ECHO, dec_msg[1], dec_msg[2], (x, y), OP_SIZE, 0)
                        else:
                            echo = message_encode(MSG_ECHO, dec_msg[1], dec_msg[2], (x, y))
                        peer.sendto(echo, n[0])
                receivedEchoReps.append(0)

    elif(dec_msg[0] == MSG_ECHO_REPLY):
        if not ((dec_msg[1], dec_msg[2])) in knownWaves:
            window.writeln("Something went wrong")
        else:
            index = knownWaves.index((dec_msg[1], dec_msg[2]))
            receivedEchoReps[index] += 1
            if(not (types[index] == dec_msg[4])):
                pass
            elif(dec_msg[4] == OP_SIZE):
                recPayload[index] += int(dec_msg[5])
            if(receivedEchoReps[index] == len(nodes) - 1):
                if(knownWaves[index][1] == (x, y)):
                    pass
                else:
                    if(types[index] == OP_SIZE):
                        msg = message_encode(MSG_ECHO_REPLY, dec_msg[1], dec_msg[2], \
                                (x, y), OP_SIZE, recPayload[index] + 1)
                    else:
                        msg = message_encode(MSG_ECHO_REPLY, dec_msg[1], dec_msg[2], (x, y))
                    peer.sendto(msg, father[index])
            elif(receivedEchoReps[index] == len(nodes) and knownWaves[index][1] == (x, y)):
                window.writeln("Echo finished.")
                if(dec_msg[4] == OP_SIZE):
                   window.writeln("Total size of the network: " + str(recPayload[index] + 1))



if __name__ == '__main__':
    sys.exit(main(sys.argv))
