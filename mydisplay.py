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
    import tkinter.font as tkfont
    py3 = 1

import mydisplay_support as display_support
from socket import *

serverName = "127.0.0.1"
serverPort = 2110
peer_connections = []
chat_connections = []
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

print(peers_list)
alive = True

def accept_connections(server, top):
    try:
        while e.isSet():
            connectionSocket, addr = server.accept()
            # sends the current code to the peers
            msg = connectionSocket.recv(1024).decode()

            if msg == "___peer___":
                t = threading.Thread(target=handle_peer, args=(connectionSocket, top.Scrolledtext1, True))
                top.Scrolledtext2.configure(state=NORMAL)
                top.Scrolledtext2.insert(END, "Connection accepted from: " + str(addr) + "\n")
                top.Scrolledtext2.configure(state=DISABLED)
            elif msg == "___chat___":
                t = threading.Thread(target=handle_chat, args=(connectionSocket, top.Scrolledtext3))
                top.Scrolledtext3.configure(state=NORMAL)
                top.Scrolledtext3.insert(END, str(addr) + " has joined\n", "left")
                top.Scrolledtext3.configure(state=DISABLED)
            
            
            t.start()
            tlist.append(t)
            peer_connections.append(connectionSocket)

    except KeyboardInterrupt:
        joinAll()

def handle_chat(connectionSocket, outputpanel):
    print("chat")

def handle_peer(connectionSocket, outputpanel, send=False):
    
    escaped_chars = {
        "13": "\n",
        "127": "",
        "8": ""
    }
    
    if send:
        current = outputpanel.get(1.0, END).strip() or "___null___"
        connectionSocket.send(current.encode())
    else:
        code = connectionSocket.recv(1024).decode()
        if code != "___null___":
            outputpanel.insert(1.0, code) 
                
    while e.isSet():
        try:   
            input_text = connectionSocket.recv(1024).decode().split()
            command = input_text[0].lower()
            print(input_text)
            if command == "___null___":
                continue
                
            if command == "end":
                break

            
            index = input_text[1]

            if command == "backspace":
                index_ar = index.split(".")
                line_index = int(index_ar[0])
                char_index = int(index_ar[1]) - 1
                index_ar[1] = str(char_index)
                index = ".".join(index_ar)
                if char_index >= 0: 
                    outputpanel.delete(index)   
                # backspace reached the beginning of the line, move the line up 
                if char_index == -1 and line_index > 1:
                    index = str(line_index - 1)+".end"
                    outputpanel.delete(index)
            
            elif command == "replace":
                start = input_text[1]
                end = input_text[2]
                char = input_text[3]
                
                try:
                    text = escaped_chars[char] 
                except KeyError:
                    text = chr(int(char))

                outputpanel.delete(start, end)
                outputpanel.insert(start, str(text))

            elif command == "delete":
                outputpanel.delete(index)
            
            else:
                try:
                    char = input_text[2]
                    try:
                        text = escaped_chars[char] 
                    except KeyError:
                        text = str(chr(int(char)))   

                    outputpanel.insert(index, text)  
             
                except IndexError:
                    print("not a char")
           
        except OSError:
            break


def disconnect_peers():
    global peer_connections
    for conn in peer_connections:
        conn.send("end".encode())
        conn.shutdown(SHUT_RD)
        conn.close()

def close_connections():
    global peer_connections
    clientSocket.send("end".encode())
    clientSocket.shutdown(SHUT_RD)
    clientSocket.close()
    disconnect_peers()

already_connected = False
def connect_peers(top):
    global peer_connections
    global chat_connections
    global already_connected
    peer_conn = None
    if not already_connected:
        try:
            for peer in peers_list:
                server = peer.split(",")[0]
                socket_number = int(peer.split(",")[1])
                peer_socket = socket(AF_INET,SOCK_STREAM)
                peer_socket.connect((server,socket_number)) 
                peer_socket.send("___peer___".encode()) 
                
                top.Scrolledtext2.configure(state=NORMAL)
                top.Scrolledtext2.insert(END, "Connected to peer: " + server + "\n")
                top.Scrolledtext2.configure(state=DISABLED) 
               
                t = threading.Thread(target=handle_peer, args=(peer_socket, top.Scrolledtext1))
                t.start()
                tlist.append(t)
                
                chat_socket = socket(AF_INET, SOCK_STREAM)
                chat_socket.connect((server,socket_number))
                chat_socket.send("___chat___".encode())
                
                t = threading.Thread(target=handle_chat, args=(chat_socket, top.Scrolledtext3))
                t.start()
                tlist.append(t)
                
                top.Scrolledtext3.configure(state=NORMAL)
                top.Scrolledtext3.insert(END, "Connected to chat: " + server + "\n", "right")
                top.Scrolledtext3.configure(state=DISABLED)
                
                peer_connections.append(peer_socket)
                chat_connections.append(chat_socket)
                already_connected = True

        except OSError as e:
                print("Socket err", e)

def vp_start_gui():
    """Starting point when module is the main routine."""
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
    """Starting point when module is imported by another program."""
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = CodeSharer (w)
    display_support.init(w, top, *args, **kwargs)
    return (w, top)

def handle_tab(event):
    print("tab Event")

def hande_keyboard(event):
    start = None
    end = None
    input_text = ""
   
    try:
        input_text = str(ord(event.char))
        start = event.widget.index(SEL_FIRST)
        end = event.widget.index(SEL_LAST)
    except TypeError:
        print("not a char")
    except TclError:
        print("nothing is selected")
        

    index = event.widget.index(INSERT)

    if start and end:
        to_send = "replace " + start + " " + end + " " + input_text
    else:
        to_send = event.keysym + " " + index + " " + input_text
    
    send_update(to_send)
    return

def send_update(to_send):
    for conn in peer_connections:
        conn.send(to_send.encode())

def run_code(input, outputLabel, language):
    code = input.get(1.0, END)
    if code.strip() and code:
        toSend = language + " " + code
        clientSocket.send(toSend.encode())
        output = clientSocket.recv(1024).decode()
        outputLabel.configure(state=NORMAL)
        outputLabel.insert(END, output)
        outputLabel.configure(state=DISABLED)
    else:
        outputLabel.configure(state=NORMAL)
        outputLabel.insert(END, "Empty file")
        outputLabel.configure(state=DISABLED)
    outputLabel.see(END)

def send_message(entry, box):
    message = entry.get()
    if not message == "" and not message == None:
        box.configure(state=NORMAL)
        box.insert(END, message + " - me\n", "right")
        box.configure(state=DISABLED)
        entry.delete(0,END)
        box.see(END)

class CodeSharer:
    def __init__(self, top=None):
        """This class configures and populates the toplevel window.
           top is the toplevel containing window."""
        _bgcolor = "#d9d9d9"  # X11 color: "gray85"
        _fgcolor = "#000000"  # X11 color: "black"
        _compcolor = "#d9d9d9" # X11 color: "gray85"
        _ana1color = "#d9d9d9" # X11 color: "gray85"
        _ana2color = "#d9d9d9" # X11 color: "gray85"
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use("winnative")
        self.style.configure(".",background=_bgcolor)
        self.style.configure(".",foreground=_fgcolor)
        self.style.map(".",background=
            [("selected", _compcolor), ("active",_ana2color)])

        top.geometry("772x539+503+177")
        top.title("CodeSharer")

        self.Button1 = Button(top)
        self.Button1.place(relx=0.48, rely=0.02, height=26, width=50)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(command=(lambda : run_code(self.Scrolledtext1, self.Scrolledtext2,display_support.combobox)))
        self.Button1.configure(text="""Run""")


        self.Button1 = Button(top)
        self.Button1.place(relx=0.60, rely=0.02, height=26, width=120)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(command=(lambda : connect_peers(self)))
        self.Button1.configure(text="""Connect to peers""")


        self.Label2 = Label(top)
        self.Label2.place(relx=0.0, rely=0.95, height=28, width=766)
        self.Label2.configure(anchor=W)
        self.Label2.configure(justify=LEFT)
        self.Label2.configure(text="""Who"s typing:""")
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
        self.Scrolledtext1.configure(tabs=tkfont.Font(font=self.Scrolledtext1['font']).measure(" "*4))
        self.Scrolledtext1.configure(undo="1")
        self.Scrolledtext1.configure(width=10)
        self.Scrolledtext1.configure(wrap=NONE)
        self.Scrolledtext1.bind("<Key>", hande_keyboard)

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
        self.Scrolledtext3.tag_configure("right", justify="right")
        self.Scrolledtext3.tag_configure("left", justify="left")
        self.Scrolledtext3.configure(state=DISABLED)

        self.Button2 = Button(top)
        self.Button2.place(relx=0.92, rely=0.89, relheight=0.05, relwidth=.08)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(text='''Send''')
        self.Button2.configure(command=(lambda: send_message(self.Entry1,self.Scrolledtext3)))

        self.Entry1 = Entry(top)
        self.Entry1.place(relx=0.52, rely=0.89, relheight=0.05, relwidth=0.4)
        self.Entry1.configure(background="white")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(width=306)
        self.Entry1.bind("<Key-Return>", (lambda x: send_message(self.Entry1,self.Scrolledtext3)))
        self.Entry1.bind("<Key-KP_Enter>", (lambda x: send_message(self.Entry1,self.Scrolledtext3)))
        self.Entry1.bind("<Key-Insert>", (lambda x: send_message(self.Entry1,self.Scrolledtext3)))

        self.Label1 = Label(top)
        self.Label1.place(relx=0.52, rely=0.59, height=18, width=99)
        self.Label1.configure(text='''Chat with peers''')

# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    """Configure the scrollbars for a widget."""

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient="vertical", command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient="horizontal", command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky="nsew")
        try:
            vsb.grid(column=1, row=0, sticky="ns")
        except:
            pass
        hsb.grid(column=0, row=1, sticky="ew")

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
            if meth[0] != "_" and meth not in ("config", "configure"):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        """Hide and show scrollbar as needed."""
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
    """Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget."""
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        return func(cls, container, **kw)
    return wrapped


class ScrolledText(AutoScroll, Text):
    """A standard Tkinter Text widget with scrollbars that will
    automatically show/hide as needed."""
    @_create_container
    def __init__(self, master, **kw):
        Text.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

if __name__ == "__main__":
    vp_start_gui()
