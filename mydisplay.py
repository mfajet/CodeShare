#! /usr/bin/env python
#
# GUI module generated by PAGE version 4.8.9
# In conjunction with Tcl version 8.6
#    Apr 01, 2017 02:52:24 PM
import sys, threading
import pygments
from pygments.styles import get_style_by_name
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.lexers import HaskellLexer

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    import TKFileDialog as FileDialog
    import tkMessageBox as messagebox
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    import tkinter.font as tkfont
    import tkinter.filedialog as FileDialog
    from tkinter import messagebox

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
peers_list = []
# peers_list = clientSocket.recv(1024).decode().split()
# peer_info = peers_list[0]
# client_port = int(peer_info.split(",")[1])
# peers_list.remove(peer_info)
e = threading.Event()
e.set()
room_name = ""
peer_info=""

peer_server = socket(AF_INET,SOCK_STREAM)
peer_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
is_host = False

def syntax_highlight(lang,codebox):
    global tlist
    print(lang)
    if(lang.lower()=="haskell"):
        lexer = HaskellLexer
    else:
        lexer=PythonLexer
    def inner(lexer,codebox):
        codebox.mark_set("range_start", "1.0")
        data = codebox.get("1.0", END)
        for token, content in lex(data, lexer()):
            codebox.mark_set("range_end", "range_start + %dc" % len(content))
            codebox.tag_add(str(token), "range_start", "range_end")
            codebox.mark_set("range_start", "range_end")
    t=threading.Thread(target=inner, args=(lexer,codebox))
    t.start()
    tlist.append(t)

def join_room(room, message, s,label):
    global peers_list
    global peer_info
    global room_name
    global client_port
    clientSocket.send(room.encode())
    potential_list = clientSocket.recv(1024).decode().split()
    if potential_list[0] == "NEW_ROOM":
        peer_info = potential_list[2]
        room_name = potential_list[1]
        label.insert(END, room_name)
        label.configure(relief=FLAT,  state='readonly')
        peers_list = []
    else:
        label.insert(END, room)
        label.configure(relief=FLAT,  state='readonly')
        peers_list = potential_list
        peer_info = peers_list[0]
        client_port = int(peer_info.split(",")[1])
        peers_list.remove(peer_info)
    client_port = int(peer_info.split(",")[1])
    connect_peers(s)
    try:
        peer_server.bind((serverName, client_port))
        peer_server.listen(1)
        is_host = True
        t = threading.Thread(target=accept_connections, args=(peer_server, s))
        t.start()
        tlist.append(t)
    except OSError:
        joinAll()
    message.destroy()

def create_room(message, top,label):
    print("Room will be created")
    global peers_list
    global peer_info
    global room_name
    global client_port
    global is_host
    clientSocket.send("NEW_ROOM".encode())
    reply = clientSocket.recv(1024).decode().split()
    room_name = reply[1]
    peers_list = []
    peer_info = reply[2]
    client_port = int(peer_info.split(",")[1])

    try:
        peer_server.bind((serverName, client_port))
        peer_server.listen(1)
        is_host = True
        t = threading.Thread(target=accept_connections, args=(peer_server, top))
        t.start()
        tlist.append(t)
    except OSError:
        joinAll()
    print(room_name)
    label.insert(END, room_name)
    label.configure(relief=FLAT,  state='readonly')

    message.destroy()


def joinAll():
    for t in tlist:
        print("closing thread:", t)
        t.join(timeout=1)


print(peers_list)

def accept_connections(server, top):
    try:
        while e.isSet():
            t = None
            connection, addr = server.accept()
            message = connection.recv(1024).decode()

            if message == "___stop___":
                connection.close()
                connection = None
                break

            if message == "___peer___":
                t = threading.Thread(target=handle_peer, args=(connection, top.Scrolledtext1, top.LineNum, True))
                top.Scrolledtext2.configure(state=NORMAL)
                top.Scrolledtext2.insert(END, "Connection accepted from: " + str(addr) + "\n")
                top.Scrolledtext2.configure(state=DISABLED)
                peer_connections.append(connection)
            elif message == "___chat___":
                chat_connections.append(connection)
                t = threading.Thread(target=handle_chat, args=(connection, top.Scrolledtext3))
                top.Scrolledtext3.configure(state=NORMAL)
                top.Scrolledtext3.insert(END, str(addr) + " has joined\n", "left")
                top.Scrolledtext3.configure(state=DISABLED)
            t.start()
            tlist.append(t)

    except KeyboardInterrupt:
        joinAll()

def handle_chat(chat, outputpanel):
    while e.isSet():
        try:
            message_ar = chat.recv(1024).decode().split("___space___")
            if message_ar[0] == "___end___":
                chat_connections.remove(chat)
                try:
                    chat.send(("___end______space___" + gethostname()).encode())
                except OSError:
                    print("socket already closed")
                    break
                outputpanel.configure(state=NORMAL)
                outputpanel.insert(END, message_ar[1] + " has left the chat", "left")
                outputpanel.configure(state=DISABLED)

                break
            outputpanel.configure(state=NORMAL)
            outputpanel.insert(END, message_ar[0] + ": " + message_ar[1] + "\n", "left")
            outputpanel.configure(state=DISABLED)
            outputpanel.see(END)
        except OSError as err:
            print("socket error", err)
    chat.close()

def handle_peer(codeshare, outputpanel, LineNum, send=False):

    escaped_chars = {
        "13": "\n",
        "127": "",
        "8": ""
    }

    if send:
        current = outputpanel.get(1.0, END).strip() or "___null___"
        codeshare.send(current.encode())
    else:
        code = codeshare.recv(1024).decode()
        print(code)
        if code != "___null___":
            outputpanel.insert(1.0, code)

    while e.isSet():
        try:
            input_text = codeshare.recv(1024).decode().split()

            if not input_text:
                break

            command = input_text[0].lower()
            print(input_text)

            if command == "___end___":
                peer_connections.remove(codeshare)
                codeshare.settimeout(1)
                codeshare.send("___end___".encode())
                print("ending connection")
                break

            index = input_text[1]
            LineNum.redraw()
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

                    if text==' ' or text =='\n' or text == '\r' or text =='\t' or text=='(' or text =='\'' or text =='"':
                        syntax_highlight(display_support.combobox,outputpanel)
                    outputpanel.insert(index, text)

                except IndexError:
                    print("not a character")

        except OSError:
            break
    codeshare.close()

def disconnect_peers():
    global peer_connections
    global chat_connections
    for conn in peer_connections:
        conn.send("___end___".encode())
        conn.close()

    for conn in chat_connections:
        conn.send(("___end______space___" + gethostname()).encode())
        conn.close()

def close_connections():
    global peer_connections
    disconnect_peers()
    clientSocket.send("___end___".encode())
    clientSocket.close()


def handle_close():
    global root
    global is_host
    e.clear()
    close_connections()
    if is_host:
        stop_server()
    joinAll()
    root.destroy()
    root = None



def stop_server():
    global client_port
    closing = socket(AF_INET,SOCK_STREAM)
    closing.connect(("", client_port))
    closing.send("___stop___".encode())
    closing.close()

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

                t = threading.Thread(target=handle_peer, args=(peer_socket, top.Scrolledtext1, top.LineNum))

                t.start()
                tlist.append(t)

                chat_socket = socket(AF_INET, SOCK_STREAM)
                chat_socket.connect((server,socket_number))
                chat_socket.send("___chat___".encode())

                t1 = threading.Thread(target=handle_chat, args=(chat_socket, top.Scrolledtext3))
                t1.start()
                tlist.append(t1)

                top.Scrolledtext3.configure(state=NORMAL)
                top.Scrolledtext3.insert(END, "Connected to peer: " + server + "\n", "right")
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


    ######This code taken from https://mail.python.org/pipermail/tkinter-discuss/2015-August/003762.html
    try:
        root.tk.call('tk_getOpenFile', '-foobarbaz')
    except TclError:
        pass
    # now set the magic variables accordingly
    root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
    root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
    #####################################################


    root.mainloop()

w = None
def create_CodeSharer(root, *args, **kwargs):
    """Starting point when module is imported by another program."""
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = CodeSharer (w)
    display_support.init(w, top, *args, **kwargs)
    return (w, top)

def handle_keyboard(event, LineNum):
    LineNum.redraw()
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

    try:
        char = chr(int(input_text))
        if char==' ' or char =='\n' or char == '\r' or char =='\t'  or char=='(' or char =='\'' or char =='"':
            syntax_highlight(display_support.combobox,event.widget)
    except:
        pass

    if start and end:
        to_send = "replace " + start + " " + end + " " + input_text
    else:
        to_send = event.keysym + " " + index + " " + input_text

    broadcast_code(to_send)
    return

def broadcast_code(to_send):
    for conn in peer_connections:
        conn.send(to_send.encode())

def broadcast(to_send):
    for conn in chat_connections:
        # TODO: change hostname by username
        message = gethostname() + "___space___" + to_send
        conn.send(message.encode())

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
    if message and not message == None:
        broadcast(message)
        box.configure(state=NORMAL)
        box.insert(END, message + " - me\n", "right")
        box.configure(state=DISABLED)
        entry.delete(0,END)
        box.see(END)

def load_file(code_textbox):
    fname = FileDialog.askopenfilename(filetypes=(("Haskell files", "*.hs"),
                                           ("Python files", "*.py;*.pyc"),
                                           ("All files", "*.*") ))
    if fname:
        text = ""
        try:
            f = open(fname,"r")
            while True:
                data = f.read()
                if (not data or data == '' or len(data) <= 0):
                    f.close()
                    break
                text+=data
            code_textbox.delete(1.0,END)
            code_textbox.insert(END,text)
        except:                     # <- naked except is a bad idea
            showerror("Open Source File", "Failed to read file\n'%s'" % fname)
        return

def change_style(name, lang, box):
    print("Name" + name)
    for tag in box.tag_names():
        box.tag_delete(tag)
    try:
        style = get_style_by_name(name)
    except:
        style = get_style_by_name('default')


    for token, predefined in style:
        if predefined['color']:
            color = "#" + predefined['color']
        else:
            color = None
        box.tag_configure(str(token), foreground=color)
    syntax_highlight(lang,box)

class CodeSharer:
    def __init__(self, top=None):
        """This class configures and populates the toplevel window.
           top is the toplevel containing window."""
        _bgcolor = "#d9d9d9"  # X11 color: "gray85"
        _fgcolor = "#000000"  # X11 color: "black"
        _compcolor = "#d9d9d9" # X11 color: "gray85"
        _ana1color = "#d9d9d9" # X11 color: "gray85"
        _ana2color = "#d9d9d9" # X11 color: "gray85"
        font11 = "-family {Bitstream Vera Sans} -size 14 -weight "  \
            "normal -slant roman -underline 0 -overstrike 0"
        font9 = "-family {Bitstream Vera Sans} -size 21 -weight normal"  \
            " -slant roman -underline 0 -overstrike 0"
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
        self.Button1.place(relx=0.79, rely=0.01, height=26, width=50)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(command=(lambda : run_code(self.Scrolledtext1, self.Scrolledtext2,display_support.combobox)))
        self.Button1.configure(text="""Run""")

        global room_name
        self.RoomLabel = Entry(top)
        self.RoomLabel.configure(background="#d9d9d9", bd=0, highlightthickness=0)
        self.RoomLabel.place(relx=0.60, rely=0.02, height=26, width=120)
        self.RoomLabel.insert(END, "Room: " )


        self.Label2 = Label(top)
        self.Label2.place(relx=0.0, rely=0.95, height=28, width=766)
        self.Label2.configure(anchor=W)
        self.Label2.configure(justify=LEFT)
        self.Label2.configure(text="""Who's typing:""")
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
        self.Scrolledtext1.configure(padx="20")
        self.Scrolledtext1.bind("<Key>", lambda e: handle_keyboard(e,self.LineNum))
        #self.Scrolledtext1.bind("<KeyRelease>",lambda e: syntax_highlight(display_support.combobox,self.Scrolledtext1))
        # self.Scrolledtext1.tag_configure("Token.Keyword", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Keyword.Constant", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Keyword.Declaration", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Keyword.Namespace", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Keyword.Pseudo", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Keyword.Reserved", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Keyword.Type", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Name.Class", foreground="#003D99")
        # self.Scrolledtext1.tag_configure("Token.Name.Exception", foreground="#003D99")
        # self.Scrolledtext1.tag_configure("Token.Name.Function", foreground="#003D99")
        # self.Scrolledtext1.tag_configure("Token.Operator.Word", foreground="#660029")
        # self.Scrolledtext1.tag_configure("Token.Comment.Multi", foreground="#3d3d3d")
        # self.Scrolledtext1.tag_configure("Token.Comment.Single", foreground="#3d3d3d")
        # self.Scrolledtext1.tag_configure("Token.Literal.String", foreground="#248F24")

        # The following is the list of styles that can be used
        #TODO: Make style selectable?
        #['manni', 'igor', 'lovelace', 'xcode', 'vim', 'autumn', 'abap', 'vs', 'rrt',
        #'native', 'perldoc', 'borland', 'arduino', 'tango', 'emacs', 'friendly',
        #'monokai', 'paraiso-dark', 'colorful', 'murphy', 'bw', 'pastie', 'rainbow_dash',
        #'algol_nu', 'paraiso-light', 'trac', 'default', 'algol', 'fruity']

        style = get_style_by_name('default')

        for token, predefined in style:
            if predefined['color']:
                color = "#" + predefined['color']
            else:
                color = None
            self.Scrolledtext1.tag_configure(str(token), foreground=color)
        self.LineNum = TextLineNumbers(self.Scrolledtext1)
        self.LineNum.attach(self.Scrolledtext1)
        self.LineNum.redraw()
        self.LineNum.place(x=-20, y=-1, relheight=1, width=20)

        self.TCombobox1 = ttk.Combobox(top)
        self.TCombobox1.place(relx=0.34, rely=0.02, relheight=0.03
                , relwidth=0.23)
        self.value_list = ["python2","python3","Haskell"]
        self.TCombobox1.configure(values=self.value_list)
        self.TCombobox1.configure(textvariable=display_support.combobox)
        self.TCombobox1.configure(takefocus="")
        self.TCombobox1.current(1)

        def langselection(e):
            display_support.combobox = self.TCombobox1.get()

        self.TCombobox1.bind("<<ComboboxSelected>>", langselection)

        self.TCombobox2 = ttk.Combobox(top)
        self.TCombobox2.place(relx=0.10, rely=0.02, relheight=0.03
                , relwidth=0.23)
        self.TCombobox2.configure(values=['manni', 'igor', 'lovelace', 'xcode', 'vim', 'autumn', 'abap', 'vs', 'rrt',
        'native', 'perldoc', 'borland', 'arduino', 'tango', 'emacs', 'friendly',
        'monokai', 'paraiso-dark', 'colorful', 'murphy', 'bw', 'pastie', 'rainbow_dash',
        'algol_nu', 'paraiso-light', 'trac', 'default', 'algol', 'fruity'])
        self.TCombobox2.configure(textvariable=style)
        self.TCombobox2.configure(takefocus="")
        self.TCombobox2.current(26)

        self.TCombobox2.bind("<<ComboboxSelected>>", lambda e : change_style(self.TCombobox2.get(),display_support.combobox, self.Scrolledtext1))

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

        self.Button3 = Button(top)
        self.Button3.place(relx=00, rely=0.0, relheight=0.05, relwidth=.08)
        self.Button3.configure(activebackground="#d9d9d9")
        self.Button3.configure(text='''Open''')
        self.Button3.configure(command=(lambda: load_file(self.Scrolledtext1)))

        self.Message1 = Message(top)
        self.Message1.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=1.0)
        self.Message1.configure(anchor=N)
        self.Message1.configure(font=font9)
        self.Message1.configure(pady="10")
        self.Message1.configure(text='''Join a coding room''')
        self.Message1.configure(width=773)

        self.Label6 = Label(self.Message1)
        self.Label6.place(relx=0.37, rely=0.20, height=28, width=50)
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(text='''Room #''')

        self.Label4 = Label(self.Message1)
        self.Label4.place(relx=0.38, rely=0.15, height=28, width=206)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(font=font11)
        self.Label4.configure(text='''Join an existing room''')

        self.Entry2 = Entry(self.Message1)
        self.Entry2.place(relx=0.42, rely=0.20, relheight=0.05, relwidth=0.25)
        self.Entry2.configure(background="white")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(width=306)

        self.Button4 = Button(self.Message1)
        self.Button4.place(relx=0.47, rely=0.25, height=26, width=65)
        self.Button4.configure(activebackground="#d9d9d9")
        self.Button4.configure(text='''Join''')
        self.Button4.configure(command=(lambda : join_room(self.Entry2.get(), self.Message1, self, self.RoomLabel)))


        self.Label5 = Label(self.Message1)
        self.Label5.place(relx=0.38, rely=0.33, height=28, width=206)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(font=font11)
        self.Label5.configure(text='''Create a new room''')

        self.Button5 = Button(self.Message1)
        self.Button5.place(relx=0.47, rely=0.42, height=26, width=65)
        self.Button5.configure(activebackground="#d9d9d9")
        self.Button5.configure(text='''Create''')
        self.Button5.configure(command=(lambda: create_room(self.Message1, self, self.RoomLabel)))




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


######Taken from http://stackoverflow.com/a/16375233
class TextLineNumbers(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw",font=self.textwidget['font'], text=linenum)
            i = self.textwidget.index("%s+1line" % i)

if __name__ == "__main__":
    vp_start_gui()
