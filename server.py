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
piers_list = []
pier_base_port = 3000

def clientThread(connectionSocket, addr):
    pier = None
    try:
        print ("Thread Client Entering Now...")
        # print (addr)
        host, socket = addr
        
        pier = host + "," + str(pier_base_port + len(piers_list))
        piers_list.insert(0, pier)        
        to_send = " ".join(piers_list) 
        connectionSocket.send(to_send.encode())
        print(piers_list)
        while True:
            f = open("tempFile",'w')
            # print("inside while loop")
            msg = connectionSocket.recv(1024).decode()
            if msg == "end":
                break
                
            f.write(msg[8:])
            f.close()
            try:
                cmd = 'python3 tempFile'
                p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                output = p.stdout.read()
            except:
                output = "Unexpected error".encode()
            connectionSocket.send(output)
    
    
        piers_list.remove(pier)
        print(piers_list)
    
    except OSError as e:
        # A socket error
          print("Socket error:",e)
          piers_list.remove(pier)
          print(piers_list)


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
