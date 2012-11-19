import socket
import gui
import time
import select
import sys

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 12345))
    client.setblocking(0)
    w = gui.MainWindow()
    while w.update():
       	try:
            while 1:
                data = client.recv(2048)
                if data: 
                    w.writeln(data)
                else:
                    break
        except:
            pass 
        try:
            line = w.getline()
            if data:
                client.sendall(line)
        except:
            pass

if __name__ == "__main__":
    main()
