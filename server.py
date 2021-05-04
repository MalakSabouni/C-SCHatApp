import math
import socket,time
import threading
import os


HEADER = 64#to get msg size

PORT = 8080
SERVER = socket.gethostbyname(socket.gethostname())
Ip = socket.gethostbyname(SERVER)

ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
NEWACCOUNT="NEW"
LOGIN="LOGIN"
SUCCESS="SUCCESS"
FAIL="FAIL"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server.bind(ADDR)
users= []
list_of_clients=[]
publicroom = []
publicUsers=[]
onlineClients=[]
privateState=False
def handle_client(conn,addr):
    connect=True
    while connect:
        msg = recieve(conn)
        if msg == DISCONNECT_MESSAGE:
            connect=False
        if msg == NEWACCOUNT:
            signup(conn)
        if msg == LOGIN:
            login(conn)
    conn.close()
    SERVER.close()



def recieve(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    msg1=''
    if msg_length:
        msg_length = int(msg_length)
        msg1 = conn.recv(msg_length).decode(FORMAT)
    return msg1

def start():
    server.listen(100)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        list_of_clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        print(f"[NEW CONNECTION] {addr} connected.")
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

def signup(conn):
    username = recieve(conn)
    state = validation(username)
    if (state):
        users.append(username)
        password = recieve(conn)
        users.append(password)
        conn.send(SUCCESS.encode(FORMAT))

    else:
        conn.send(FAIL.encode(FORMAT))
def login(conn):
    username = recieve(conn)
    passw = recieve(conn)
    state = loginV(username, passw)
    if (state):
        conn.send(SUCCESS.encode(FORMAT))
        chatType = recieve(conn)
        if chatType == '1':
            publicUsers.append(conn)
            public(conn, username)
        elif chatType == '2':
            global privateBook
            privateBook=True
            onlineClients.append(conn)
            msg=recieve(conn)
            if msg=="w":
                private(conn,username,1)
            elif msg=="JUSTWAIT":
                x=recieve(conn)
                if x=="OK":
                    private(conn,username,0)

        else:
            conn.close()
    else:
        conn.send(FAIL.encode(FORMAT))

def validation(msg):
    i=0
    while i<len(users):
        if users[i] ==msg:
            return False
        i+=2

    return True

def loginV(msg,passw):
    i = 0
    for u in users:
        if u==msg:
            return users[i+1]==passw
        else:
            i+=1
    return False

def public(conn,username):
    conn.send("You are in public chat,Enter exit0 to exit".encode(FORMAT))
    connect = True
    publicroom.append(conn)
    hey=f'{username} join with you\n'
    print(hey)
    broadcast(hey,conn)
    while connect:
        try:
            msg=recieve(conn)
            if msg:
                if msg == "exit":
                    connect = False
                else:
                    msg = f'{username}: {msg}\n'
                    broadcast(msg,conn)
        except:
            continue

def private(conn,username,direct):
    while True:
        dest= recieve(conn)
        for i in onlineClients:
            print("check private connection..")
            if str(i.getpeername())== dest.strip() and i!=conn:
                if direct==1:
                    print(SUCCESS)
                    i.send(f"{username}  want to chat with you".encode(FORMAT))
                    x=conn.getpeername()
                    i.send(f"{x}".encode(FORMAT))
                    conn.send(SUCCESS.encode(FORMAT))
                    chat(i,conn)
                else:

                    chat(i,conn)
        print("FAIL, client will try again..")
        conn.send("Fail".encode(FORMAT))






def broadcast(message, conn):
    for clients in publicroom:
        try:
            if clients != conn:
                clients.send(message.encode(FORMAT))
        except:
            clients.close()
            # if the link is broken, we remove the client
            remove(clients)

def chat(destcon,conn):
    connect=True
    while connect:
        try:
            msg = recieve(conn)
            if msg:
                if msg == "exit":
                    connect = False
                    if conn in onlineClients:
                        onlineClients.remove(conn)
                elif msg=="l":
                    fileexc= recieve(conn)
                    destcon.send("RECIEVE".encode(FORMAT))
                    agree=recieve(destcon)
                    if agree=="OK":
                        destcon.send(fileexc.encode(FORMAT))
                        time.sleep(10)
                        print("establish with dest succ")
                        while True:
                            print("turn data")
                            data =conn.recv(1024)
                            destcon.send(data)
                            if not data:
                                break
                            if data==None:
                                break

                        print('Successfully get the file')
                    else:
                        conn.send("Your friend refused the file, sending failed.".encode(FORMAT))

                else:
                    msg = f'{msg}\n'
                    destcon.send(msg.encode(FORMAT))
        except:
            continue

"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""


def remove(connection):
    if connection in publicroom:
        publicroom.remove(connection)

print("[STARTING] server is starting...")
start()

