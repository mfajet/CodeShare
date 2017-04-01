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

def clientThread(connectionSocket, addr):

    try:
        print ("Thread Client Entering Now...")
        print (addr)
        while True:
            f = open("tempFile",'w')

            msg = connectionSocket.recv(1024).decode()
            f.write(msg)
            f.close()
            try:
                cmd = 'python3 tempFile'
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()
            except:
                output = "Unexpected error".encode()
            connectionSocket.send(output)
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
