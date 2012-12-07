# Netwerken en Systeembeveiliging
# Lab 8 - Distributed Sensor Network
# Author(s) and student ID(s):
# Group:
# Date:
import sys
import struct
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

	## Create the peer-to-peer socket.
	peer = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	# Set the socket multicast TTL so it can send multicast messages.
	peer.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 2)
	# Bind the socket to a random port.
	peer.bind(('', INADDR_ANY))

	## This is the event loop.
	window = MainWindow()
	while window.update():
		pass



if __name__ == '__main__':
	sys.exit(main(sys.argv))
