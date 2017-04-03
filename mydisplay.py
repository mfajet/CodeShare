#! /usr/bin/env python
#
# GUI module generated by PAGE version 4.8.9
# In conjunction with Tcl version 8.6
#    Apr 01, 2017 02:52:24 PM
import sys, threading

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

import mydisplay_support as display_support
from socket import *

serverName = '127.0.0.1'
serverPort = 2110
peer_connections = []
tlist = []
clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
peers_list = clientSocket.recv(1024).decode().split()
peer_info = peers_list[0]
client_socket = int(peer_info.split(",")[1])
peers_list.remove(peer_info)
e = threading.Event()
e.set()


def joinAll():
    for t in tlist:
        print("closing thread:", t)
        t.join(timeout=1)

try:
    peer_server = socket(AF_INET,SOCK_STREAM)
    peer_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    peer_server.bind((serverName, client_socket))
    peer_server.listen(1)
except OSError:
    joinAll()

sent_buffer_count = 0

print(peers_list)
alive = True
def accept_connections(server, top):
    try:
        while e.isSet():
            connectionSocket, addr = server.accept()
            # sends the current code to the peers
            connectionSocket.send(top.Scrolledtext1.get(1.0, END).encode())
            t = threading.Thread(target=handle_connection, args=(connectionSocket, top))
            top.Scrolledtext2.configure(state=NORMAL)
            top.Scrolledtext2.insert(END, "Connection accepted from: " + str(addr) + "\n")
            top.Scrolledtext2.configure(state=DISABLED)
            t.start()
            tlist.append(t)
            peer_connections.append(connectionSocket)
    except KeyboardInterrupt:
        joinAll()

def handle_connection(connectionSocket, top):
    while e.isSet():
        try:
            input_text = connectionSocket.recv(1024).decode().split()
            outputpanel = top.Scrolledtext1
            command = input_text[0].lower()
            print(input_text)
            if command == 'quit':
                break

            index = input_text[1]

            if command == 'backspace':
                index_ar = index.split('.')
                index_ar[1] = str(int(index_ar[1]) - 1)
                index = ".".join(index_ar)
                outputpanel.delete(index)

            elif command == 'delete':
                outputpanel.delete(index)

            elif command == 'tab':
                outputpanel.insert(index, "    ")

            elif command == 'space':
                outputpanel.insert(index, " ")

            elif command == 'return':
                outputpanel.insert(index, "\n")

            else:
                try:
                    char = input_text[2]
                    outputpanel.delete(index)
                    outputpanel.insert(index, char)
                except IndexError:
                    print("not insert key")

        except OSError:
            break

def close_connections():
    global peer_connections
    clientSocket.send("end".encode())
    clientSocket.close()
    for peer in peer_connections:
        peer.send("end".encode())
        peer.close()

already_connected = False
def connect_peers(outputpanel, top):
    global peer_connections
    global already_connected
    if not already_connected:
        try:
            for peer in peers_list:
                print(peer)
                peer_server = peer.split(",")[0]
                peer_socket = int(peer.split(",")[1])
                peer_conn = socket(AF_INET,SOCK_STREAM)
                peer_conn.connect((peer_server,peer_socket))
                code = peer_conn.recv(1024).decode()
                # loads the code from peer
                top.Scrolledtext1.insert(1.0, code)
                t = threading.Thread(target=handle_connection, args=(peer_conn, top))
                t.start()
                tlist.append(t)
                outputpanel.configure(state=NORMAL)
                outputpanel.insert(END, "Connected to peer: " + peer_server + "\n")
                outputpanel.configure(state=DISABLED)
                peer_connections.append(peer_conn)
                already_connected = True
        except KeyboardInterrupt:
                joinAll()

def disconnect_peers():
    global peer_connections
    for conn in peer_connections:
        conn.send("leaving".encode())
        conn.shutdown(SHUT_RDWR)
        conn.close()


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    top = CodeSharer (root)
    display_support.init(root, top)
    root.protocol("WM_DELETE_WINDOW", handle_close)
    t = threading.Thread(target=accept_connections, args=(peer_server, top))
    t.start()
    tlist.append(t)
    root.mainloop()


def handle_close():
    global root
    e.clear()
    root.destroy()
    close_connections()
    joinAll()

w = None
def create_CodeSharer(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = CodeSharer (w)
    display_support.init(w, top, *args, **kwargs)
    return (w, top)

def send_code(event):
    input_text = event.char
    index = event.widget.index('insert')
    to_send = event.keysym + " " + index + " " + input_text
    for conn in peer_connections:
        conn.send(to_send.encode())
    return

def run_code(input, outputLabel, language):
    code = input.get(1.0, END)
    print("to run", code)
    print(language)
    if not code.strip() == "" and not code == None:
        toSend = language + " " + code
        clientSocket.send(toSend.encode())
        output = clientSocket.recv(1024).decode()
        outputLabel.configure(state=NORMAL)
        outputLabel.insert(END, output)
        outputLabel.configure(state=DISABLED)
    else:
        outputLabel.configure(state=NORMAL)
        outputLabel.delete(1.0, END)
        outputLabel.insert(END, "Empty file")
        outputLabel.configure(state=DISABLED)


class CodeSharer:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#d9d9d9' # X11 color: 'gray85'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("772x539+503+177")
        top.title("CodeSharer")

        self.Button1 = Button(top)
        self.Button1.place(relx=0.48, rely=0.02, height=26, width=50)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(command=(lambda : run_code(self.Scrolledtext1, self.Scrolledtext2,display_support.combobox)))
        self.Button1.configure(text='''Run''')


        self.Button1 = Button(top)
        self.Button1.place(relx=0.60, rely=0.02, height=26, width=120)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(command=(lambda : connect_peers(self.Scrolledtext2, self)))
        self.Button1.configure(text='''Connect to peers''')


        self.Label2 = Label(top)
        self.Label2.place(relx=0.0, rely=0.95, height=28, width=766)
        self.Label2.configure(anchor=W)
        self.Label2.configure(justify=LEFT)
        self.Label2.configure(text='''Who's typing:''')
        self.Label2.configure(width=766)

        self.Scrolledtext1 = ScrolledText(top)

        self.Scrolledtext1.configure()
        self.Scrolledtext1.place(relx=0.0, rely=0.07, relheight=0.87
                , relwidth=0.52)
        self.Scrolledtext1.configure(background="white")
        self.Scrolledtext1.configure(font="TkTextFont")
        self.Scrolledtext1.configure(insertborderwidth="3")
        self.Scrolledtext1.configure(selectbackground="#c4c4c4")
        self.Scrolledtext1.configure(takefocus="0")
        self.Scrolledtext1.configure(tabs="    ")
        self.Scrolledtext1.configure(undo="1")
        self.Scrolledtext1.configure(width=10)
        self.Scrolledtext1.configure(wrap=NONE)
        self.Scrolledtext1.bind("<Key>", send_code)
        # self.Scrolledtext1.bind("<Tab>", send_code)

        def tab(arg):
            self.Scrolledtext1.insert(INSERT, " " * 4)
            return 'break'

        self.Scrolledtext1.bind("<Tab>", tab)

        self.TCombobox1 = ttk.Combobox(top)
        self.TCombobox1.place(relx=0.19, rely=0.02, relheight=0.03
                , relwidth=0.23)
        self.value_list = ["python2","python3","Haskell"]
        self.TCombobox1.configure(values=self.value_list)
        self.TCombobox1.configure(textvariable=display_support.combobox)
        self.TCombobox1.configure(takefocus="")
        self.TCombobox1.current(1)

        def langselection(e):
            display_support.combobox = self.TCombobox1.get()

        self.TCombobox1.bind("<<ComboboxSelected>>", langselection)


        self.Scrolledtext2 = ScrolledText(top)
        self.Scrolledtext2.place(relx=0.52, rely=0.07, relheight=0.52
                , relwidth=0.48)
        self.Scrolledtext2.configure(background="white")
        self.Scrolledtext2.configure(font="TkTextFont")
        self.Scrolledtext2.configure(insertborderwidth="3")
        self.Scrolledtext2.configure(selectbackground="#c4c4c4")
        self.Scrolledtext2.configure(undo="1")
        self.Scrolledtext2.configure(width=10)
        self.Scrolledtext2.configure(wrap=CHAR)
        self.Scrolledtext2.insert(END, '''Output will show up here\n''')
        self.Scrolledtext2.configure(state=DISABLED)

        self.Scrolledtext3 = ScrolledText(top)
        self.Scrolledtext3.place(relx=0.52, rely=0.63, relheight=0.26
                , relwidth=0.48)
        self.Scrolledtext3.configure(background="white")
        self.Scrolledtext3.configure(font="TkTextFont")
        self.Scrolledtext3.configure(insertborderwidth="3")
        self.Scrolledtext3.configure(selectbackground="#c4c4c4")
        self.Scrolledtext3.configure(undo="1")
        self.Scrolledtext3.configure(width=10)
        self.Scrolledtext3.configure(wrap=WORD)
        self.Scrolledtext3.configure(state=DISABLED)

        self.Button2 = Button(top)
        self.Button2.place(relx=0.92, rely=0.89, relheight=0.05, relwidth=.08)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(text='''Send''')

        self.Entry1 = Entry(top)
        self.Entry1.place(relx=0.52, rely=0.89, relheight=0.05, relwidth=0.4)
        self.Entry1.configure(background="white")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(width=306)

        self.Label1 = Label(top)
        self.Label1.place(relx=0.52, rely=0.59, height=18, width=99)
        self.Label1.configure(text='''Chat with peers''')

# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = Pack.__dict__.keys() | Grid.__dict__.keys() \
                  | Place.__dict__.keys()
        else:
            methods = Pack.__dict__.keys() + Grid.__dict__.keys() \
                  + Place.__dict__.keys()

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        return func(cls, container, **kw)
    return wrapped


class ScrolledText(AutoScroll, Text):
    '''A standard Tkinter Text widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        Text.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

if __name__ == '__main__':
    vp_start_gui()
