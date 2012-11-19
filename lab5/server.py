import socket
import select
import sys

def_names = ["Frits", "Olivier", "Roderique", "Jan-Willem", "Frederik",
    "Sjors", "Frans", "Alexander", "Dominique", "Jan-Frits"]
clients = {}

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 12345))
    input = [server]
    server.listen(10)
    while 1:
        ready_client, _, _ =  select.select(input,[],[])
        for desc in ready_client:
            if desc == server:
                client, _ = server.accept()
                input.append(client)
                count = len(clients)
                while(not free_name(def_names[count])):
                    count += 1
                    count %= 10
                clients[client] = def_names[count]
                print_to_all("[SERVER] " + clients[client] + " is binnengekomen.")
            else:
                incoming = desc.recv(2048)
                if incoming:
                    invoer = incoming.split(" ")
                    if(invoer[0] == "/nick"):
                        nick_cmd(invoer, desc)
                    elif(invoer[0] == "/say"):
                        say_cmd(" ".join(invoer[1:]), desc)
                    elif(invoer[0] == "/whisper"):
                        whisper_cmd(invoer, desc)
                    elif(invoer[0] == "/list"):
                        print_list(invoer, desc)
                    elif(invoer[0][0] == "/"):
                        desc.sendall("[ERROR] Deze opdracht bestaat niet!")
                    else:
                        say_cmd(incoming, desc)
                else:
                    print_to_all("[SERVER] " + clients[desc] + " heeft de chat verlaten.")
                    input.remove(desc)
                    del clients[desc]
                    desc.close()

def print_to_all(data):
    for client in clients.keys():
        client.sendall(data)

def print_to_one(data, send, rec):
    message = "[Privebericht (" + clients[send] + " -> " + rec + ")]: " + data
    send.sendall(message)
    for client in clients.keys():
        if clients[client] == rec:
            client.sendall(message)

def free_name(n):
    if n in clients.values():
        return False
    return True

def nick_cmd(text, send):
    if len(text) > 2 or len(text) < 2:
        send.sendall("[ERROR] Gebruik: /nick <naam>")
    elif(not free_name(text[1])) :
        send.sendall("[ERROR] Deze gebruikersnaam bestaat al!")
    else:
        print_to_all("[SERVER] " + clients[send] + " heet nu " + text[1])
        clients[send] = text[1]

def whisper_cmd(text, send):
    if len(text) < 3:
        send.sendall("[ERROR] Gebruik: /whisper <nick> <message>")
    elif(free_name(text[1])):
        send.sendall("[ERROR] Deze gebruiker is niet online!")
    elif(text[1] == clients[send]):
        send.sendall("[ERROR] Wil je nou echt in jezelf praten?")
    else:
        print_to_one(" ".join(text[2:]), send, text[1])

def say_cmd(text, send):
    print_to_all(">> " + clients[send] + " zegt: " + text)

def print_list(text, send):
    data = "[" + str(len(clients)) + " online gebruiker(s)]" 
    for client in clients.keys():
        data += "\n" + clients[client]
    send.sendall(data)

if __name__ == "__main__":
    main()
