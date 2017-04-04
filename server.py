from socket import *
import threading
import time
import sys
import traceback
import errno
from subprocess import Popen, PIPE, STDOUT
import os
## global variables
tList = []
peers_list = []
chat_rooms = []
peer_base_port = 3000

def clientThread(connectionSocket, addr):
    peer = None
    try:
        print ("Thread Client Entering Now...")
        host, socket = addr

        peer = host + "," + str(peer_base_port + len(peers_list))
        peers_list.insert(0, peer)
        to_send = " ".join(peers_list)
        connectionSocket.send(to_send.encode())
        print(peers_list)
        while True:
            f = open("tempFile",'w')
            # print("inside while loop")
            msg = connectionSocket.recv(1024).decode()
            if msg == "___end___":
                break
            if msg[0:7] == "python3":
                cmd = 'python3 tempFile'
            elif msg[0:7] == "python2":
                cmd = 'python tempFile'
            elif msg[0:7].lower() =="haskell":
                cmd= 'runhaskell tempFile'
            else:
                connectionSocket.send("Unknown language".encode())
                continue

            f.write(msg[8:])
            f.close()
            try:
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()
                if(output.decode() =="" or output.decode()==None):
                    output="[No output]\n".encode()
            except:
                output = "Unexpected error\n".encode()
            connectionSocket.send(output)


        peers_list.remove(peer)
        print(peers_list)

    except OSError as e:
        # A socket error
          print("Socket error:",e)
          peers_list.remove(peer)
          print(peers_list)


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
