from socket import *
import threading
from threading import Timer

import time
import sys
import traceback
import errno
from subprocess import Popen, PIPE, STDOUT
import os
import string
import random
## global variables
tList = []
chat_rooms = []
peer_base_port = 3000
base_code_port = 10000
room_list_dict = {}
choose_from = string.ascii_letters + "0123456789"
peer_num = 0
code_num = 0

def unique_name():
    str = ""
    for x in range(6):
        str += random.choice(choose_from)
    return str

def clientThread(connectionSocket, addr):
    peer = None
    global peer_num
    room_name = None
    try:
        print ("Thread Client Entering Now...")
        host, sock = addr
        msg = connectionSocket.recv(1024).decode().split()
        room_name = msg[0]
        notif_port = msg[1]
        peer_num +=1
        peer = host + "," + str(peer_base_port + peer_num) + "," + notif_port

        print(peer)

        if room_name == "___newroom___" or not room_name in room_list_dict:
            room_name = unique_name()
            while room_name in room_list_dict:
                room_name = unique_name()
            room_list_dict[room_name] =[peer]
            connectionSocket.send(("___newroom___ " + room_name + " " + peer).encode())
        else:
            peers_list = room_list_dict[room_name]
            peers_list.insert(0, peer)
            to_send = " ".join(peers_list)
            connectionSocket.send(to_send.encode())
            room_list_dict[room_name] = peers_list
            print(peers_list)
        while True:
            global code_num
            f = open("tempFile",'w')
            # print("inside while loop")
            msg = connectionSocket.recv(1024).decode()
            if msg == "___end___":
                room_list_dict[room_name].remove(peer)
                print(room_list_dict[room_name])
                break
            elif msg[0:7] == "python3":
                cmd = 'python3 tempFile'
            elif msg[0:7] == "python2":
                cmd = 'python tempFile'
            elif msg[0:7].lower() =="haskell":
                cmd= 'runhaskell tempFile'
            else:
                connectionSocket.send("Unknown language".encode())
                continue
            code_socket = socket(AF_INET, SOCK_STREAM)
            # reuse port
            code_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            code_socket.bind(('127.0.0.1', base_code_port + code_num))
            code_socket.listen(15)
            connectionSocket.send(("127.0.0.1 " + str(base_code_port + code_num) ).encode())
            code_num +=1
            code_connection, code_host = code_socket.accept()
            f.write(msg[8:])
            while True:
                data = code_connection.recv(1024).decode()
                if (data[-9:] == "___EOF___" or not data or data == '' or len(data) <= 0):
                    f.write(data[0:-9])
                    break
                else:
                    f.write(data)
            f.close()
            try:
                output =""
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                timer = Timer(10, lambda x: x.kill(), [p])
                try:
                    timer.start()
                    output = p.stdout.read()

                finally:
                    if(not timer.isAlive()):
                        output="Execution canceled. Process took too long.\n".encode()
                    timer.cancel()


                if(output.decode() =="" or output.decode()==None):
                    output="[No output]\n".encode()
            except:
                output = "Unexpected error\n".encode()
            i = 0
            while True:
                data = output[i*1024:(i+1)*1024]
                i+=1
                if (not data or data == '' or len(data) <= 0):
                    break
                else:
                    try:
                        code_connection.send(data)
                    except:
                        code_connection.send("Unexpected error\n".encode())
            code_connection.close()

    except OSError as e:
        # A socket error
          print("Socket error:",e)


def joinAll():
    global tList
    for t in tList:
        t.join()

def main():
    try:
        global tList
        serverPort = 2110
        serverSocket = socket(AF_INET,SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serverSocket.bind(('127.0.0.1',serverPort))
        serverSocket.listen(15)
        print('The server is ready to receive')

        while True:
            connectionSocket, addr = serverSocket.accept()
            t = threading.Thread(target=clientThread,args=(connectionSocket,addr))
            t.start()
            tList.append(t)
            print("Thread started")
            print("Waiting for another connection")
    except KeyboardInterrupt:
        print ("Keyboard Interrupt. Time to say goodbye!!!")
        joinAll()
    #except Exception:
     #   traceback.print_exc(file=sys.stdout)

    print("The end")
    sys.exit(0)

if __name__ == "__main__":
    # execute only if run as a script
    main()
