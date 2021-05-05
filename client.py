import socket
import threading
import os
import select

HEADER = 64
PORT = 8080
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
# my ip public for Feature 7:7. Clients and server must not be on the same network (WiFi)
SERVER1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = "192.168.1.22"
ADDR = (client, PORT)
privateBook = False
SERVER1.connect(ADDR)


def startApp():
    print("hello that is Malak & Wajiha & Maimonah chat app project")
    while True:
        c = input("please enter 1 to login and 2 to signup\n")
        if c == '1':
            login()
        elif c == '2':
            signup()
        else:
            print("error,try again!")


def signup():
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        send("NEW")
        send(username)
        send(password)
        msg = SERVER1.recv(2048).decode(FORMAT)
        if msg == "SUCCESS":
            print(msg)
            break
        elif msg == "FAIL":
            print("username is token..try another username")
        else:
            print("uncatch error happend during sign up")
    login()


def login():
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        send("LOGIN")
        send(username)
        send(password)
        msg = SERVER1.recv(2048).decode(FORMAT)
        if msg == "SUCCESS":
            break
        elif msg == "FAIL":
            print("username or passord is incorrect..try again")
        else:
            print("uncatch error happend during login")

    target(username)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    SERVER1.send(send_length)
    SERVER1.send(message)

#chose type
def target(username):
    while True:
        c = input("choose your chatting method: Enter 1 for public chat and 2 for private chat \n 3 to exit the app")
        if c == '1':
            send('1')
            pupChat(username)
        elif c == '2':
            send('2')
            global privateBook
            privateBook = True
            x = input(
                "You are now in private room chat\n press any thing to wait for someone call you\npress you press W if you know address to contact with \n Enter exit0 to exit.. ")
            if x == "w":
                send(x.lower())
                priChat(username)
            elif x == "exit0":
                target(username)
            else:
                send("JUSTWAIT")
                print("wait..\n")
                request = SERVER1.recv(2048).decode()
                add = SERVER1.recv(2048).decode()
                send("OK")
                print(f'{request} \n')
                send(add)
                nname = input("enter nickname for your friend: ")
                chat(username, nname)



        elif c == '3':
            send('3')
            send(DISCONNECT_MESSAGE)
        else:
            print("bad input..try again")


def pupChat(username):
    connect = True
    greet = SERVER1.recv(2048).decode(FORMAT)
    print(greet)
    while connect:
        message = input(">>")
        if message == "exit0":
            connect = False
        elif message=="":
            message = SERVER1.recv(2048).decode(FORMAT)
            if message:
                print(message)
        else:
            send(message)
            print(f'{username}: {message}')

    target(username)


def priChat(username):
    global privateBook
    while privateBook:
        destUser = input("Enter the address for user you want to comunicate, or press exit0 to exit")
        if destUser == 'exit0':
            privateBook = False
        else:
            if privateBook:
                send(destUser)
                servar = SERVER1.recv(2048).decode(FORMAT)
                if servar == "SUCCESS":
                    nname = input("enter nickname for your friend: ")
                    chat(username, nname)
                else:
                    print(f"error happend during connection with {destUser} try again! ")
    target(username)


def chat(usernme, destUser):
    print(f'hi {usernme} you are in private chat with {destUser}'
          f'\n enter SHARE to share files,SEND to recieve file (only if your friend will share) and exit0 to exit\n')
    connect = True
    while connect:
        action = input(">>")
        if action == "exit0":
            send("exit")
            connect = False
        elif action== "":
            type = SERVER1.recv(6).decode(FORMAT)
            if type=="RECIVE":
                agree= input("your friend want to share file with you press Y if you are agree and anything for No")
                if agree.capitalize()=="Y":
                    send("Y")
                    type = SERVER1.recv(4).decode(FORMAT)
                    if type:
                        fname = input("enter name of file: ")
                        with open(fname + type, 'wb') as f:
                            if type == ".txt":
                                data = SERVER1.recv(2048)
                                f.write(data)
                                f.close()
                            else:
                                data = SERVER1.recv(700000000)
                                f.write(data)

                                # write data to a file

                                f.close()
                            print('Successfully get the file')
                    else:
                        print("your friend didnot share you file yet, try again")
            else:
                message = SERVER1.recv(2048).decode(FORMAT)
                print(f'{destUser}: {type+message}')


        elif action== "SHARE":
            filename = input("enter path of the file : ")
            filetype= input("enter file type, example: .png: ")
            send(action)
            send(filetype)
            f = open(filename+filetype, 'rb')
            l = f.read(2048)
            while (l):
                SERVER1.send(l)
                l = f.read(2048)
            f.close()
            state = SERVER1.recv(4).decode(FORMAT)
            if state=="SUCC":
                print('Done sending')
            else:
                print("your friend did not accept your file:| try again after informing him")

        else :
            send(action)





startApp()
