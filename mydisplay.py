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

import display_support
from socket import *

serverName = '127.0.0.1'
serverPort = 2110
pier_connections = []
tlist = []
clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
piers_list = clientSocket.recv(1024).decode().split()
pier_info = piers_list[0]
client_socket = int(pier_info.split(",")[1])
piers_list.remove(pier_info)

try:
    pier_server = socket(AF_INET,SOCK_STREAM)
    pier_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    pier_server.bind((serverName, client_socket))
    pier_server.listen(1)
except KeyboardInterrupt:
    joinAll()

sent_buffer_count = 0

print(piers_list) 

def accept_connections(server, top):
    while True:
        connectionSocket, addr = server.accept()
        t = threading.Thread(target=handle_connection, args=(connectionSocket, top))
        top.Scrolledtext2.configure(state=NORMAL)
        top.Scrolledtext2.insert(END, "Connection accepted from: " + str(addr) + "\n")
        top.Scrolledtext2.configure(state=DISABLED)
        t.start()
        tlist.append(t)
        pier_connections.append(connectionSocket)

def handle_connection(connectionSocket, top):
    while True:
        msg = connectionSocket.recv(1024).decode()
        outputpanel = top.Scrolledtext1
        outputpanel.configure(state=NORMAL)
        outputpanel.insert(END, msg)
      

def connect_piers(outputpanel, top):
    global pier_connections
    for pier in piers_list:
        print(pier)
        pier_server = pier.split(",")[0]
        pier_socket = int(pier.split(",")[1])
        pier_conn = socket(AF_INET,SOCK_STREAM)
        pier_conn.connect((pier_server,pier_socket))
        t = threading.Thread(target=handle_connection, args=(pier_conn, top))
        t.start()
        tlist.append(t)
        outputpanel.configure(state=NORMAL)
        outputpanel.insert(END, "Connected to pier: " + pier_server + "\n")
        outputpanel.configure(state=DISABLED)
        pier_connections.append(pier_conn)

def joinAll():
    for t in tlist:
        t.join()

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    top = CodeSharer (root)
    display_support.init(root, top)  
    root.protocol("WM_DELETE_WINDOW", handle_close)
    t = threading.Thread(target=accept_connections, args=(pier_server, top))
    t.start()
    tlist.append(t)
    root.mainloop()
    

def handle_close():
    global root
    clientSocket.send("end".encode())
    clientSocket.close()
    root.destroy()
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

def destroy_CodeSharer():
    global w
    joinAll()
    w.destroy()
    w = None

def send_code(event):
    global sent_buffer_count
    inputtext = event.widget.get(1.0, END).strip()
    send_buffer = inputtext[sent_buffer_count:]
    sent_buffer_count = sent_buffer_count + len(send_buffer)
    print(send_buffer)
    if send_buffer:
        for conn in pier_connections:
            print(conn)
            conn.send(send_buffer.encode())
    return 

def run_code(st, outputLabel, language):
    code = st.get(1.0, END)
    if not code.strip() == "" and not code == None:
        toSend = language + " " + code
        clientSocket.send(toSend.encode())
        output = clientSocket.recv(1024).decode()
        outputLabel.configure(state=NORMAL)
        outputLabel.insert(END, "-----------\n")
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
        self.Button1.configure(command=(lambda : connect_piers(self.Scrolledtext2, self)))
        self.Button1.configure(text='''Connect to piers''')
    

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
        self.Scrolledtext1.bind("<Leave>", send_code)

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
        self.Scrolledtext2.place(relx=0.52, rely=0.07, relheight=0.87
                , relwidth=0.48)
        self.Scrolledtext2.configure(background="white")
        self.Scrolledtext2.configure(font="TkTextFont")
        self.Scrolledtext2.configure(insertborderwidth="3")
        self.Scrolledtext2.configure(selectbackground="#c4c4c4")
        self.Scrolledtext2.configure(undo="1")
        self.Scrolledtext2.configure(width=10)
        self.Scrolledtext2.configure(wrap=NONE)
        self.Scrolledtext2.insert(END, '''Output will show up here\n''')
        self.Scrolledtext2.configure(state=DISABLED)


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


