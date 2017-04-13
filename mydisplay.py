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
from tooltip import *
from socket import *

serverName = "127.0.0.1"
serverPort = 2110
peer_connections = []
chat_connections = []
notif_peers = []
tlist = []
clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
peers_list = []
e = threading.Event()
e.set()
room_name = ""
peer_info=""
notif_port = None
client_port = None
is_host = False
peer_socket = socket(AF_INET,SOCK_STREAM)
peer_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
notif_socket = socket(AF_INET, SOCK_DGRAM)
notif_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
notif_socket.bind((serverName, 0))
username = gethostname()
loaded = False


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
    t.daemon = True
    t.start()
    tlist.append(t)

def join_room(room, message, top,label):
    global peers_list
    global peer_info
    global room_name
    global notif_port
    global peer_socket
    global notif_socket
    if room=="":
        return
    server_addr, notif_port = notif_socket.getsockname()
    clientSocket.send((room + " " + str(notif_port)).encode())
    potential_list = clientSocket.recv(1024).decode().split()
    if potential_list[0] == "___newroom___":
        peer_info = potential_list[2]
        room_name = potential_list[1]
        label.insert(END, room_name)
        label.configure(relief=FLAT,  state='readonly')
        peers_list = []
    else:
        label.insert(END, room)
        room_name = room
        label.configure(relief=FLAT,  state='readonly')
        peers_list = potential_list
        peer_info = peers_list[0]
        peers_list.remove(peer_info)
    client_port = int(peer_info.split(",")[1])
    peer_socket.bind((serverName, client_port))
    peer_socket.listen(5)
    try:
        start_server(peer_socket, notif_socket, top)
    except OSError:
        joinAll()

    connect_peers(top)
    message.destroy()

def create_room(message,top,label):
    print("Room will be created")
    global peer_info
    global room_name
    global client_port
    global is_host
    global notif_port
    global notif_socket
    global peer_socket

    server_addr, notif_port = notif_socket.getsockname()
    print(server_addr, notif_port)

    clientSocket.send(("___newroom___ " + str(notif_port)).encode())

    reply = clientSocket.recv(1024).decode().split()
    room_name = reply[1]
    peer_info = reply[2]
    client_port = int(peer_info.split(",")[1])
    peer_socket.bind((serverName, client_port))
    peer_socket.listen(5)
    is_host = True

    try:
        start_server(peer_socket, notif_socket, top)
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


def start_server(peer_socket, notif_socket, top):
    t = threading.Thread(target=client_server, args=(peer_socket, top))
    t.daemon = True
    t.start()
    t1 = threading.Thread(target=notif_server, args=(notif_socket, top))
    t1.daemon = True
    t1.start()
    tlist.append(t)
    tlist.append(t1)


def notif_server(server, top):
    global notif_peers
    chat = False
    while e.isSet():
        try:
            buffer, addr = server.recvfrom(1024)
            notif = buffer.decode()
            print(notif)
            if notif[0:10] == "___stop___":
                server.sendto("___stop___", addr)
                notif_peers.remove(addr)
                break

            if notif == "___addr___":
                notif_peers.append(addr)

            elif notif[0:10] == "___sent___":
                chat = False
                top.notif_text.configure(state=NORMAL)
                top.notif_text.delete(1.0, END)
                top.notif_text.configure(state=DISABLED)
            else:
                chat = False
                top.notif_text.configure(state=NORMAL)
                top.notif_text.delete(1.0, END)
                top.notif_text.insert(END, notif)
                top.notif_text.configure(state=DISABLED)


        except OSError:
            break
        except KeyboardInterrupt:
            break
    print("ending notif thread")


def client_server(server, top):
    while e.isSet():
        try:
            t = None
            connection, addr = server.accept()
            message = connection.recv(1024).decode()

            if message == "___stop___":
                connection.close()
                connection = None
                break

            if message == "___peer___":
                t = threading.Thread(target=handle_peer, args=(connection, top.EditorTextbox, top.LineNum, True))
                top.OutputTextbox.configure(state=NORMAL)
                top.OutputTextbox.insert(END, "Connection accepted from: " + str(addr) + "\n")
                top.OutputTextbox.configure(state=DISABLED)
                peer_connections.append(connection)
            elif message == "___chat___":
                chat_connections.append(connection)
                t = threading.Thread(target=handle_chat, args=(connection, top.ChatMessagesTextbox))
                top.ChatMessagesTextbox.configure(state=NORMAL)
                top.ChatMessagesTextbox.insert(END, str(addr) + " has joined\n", "left")
                top.ChatMessagesTextbox.configure(state=DISABLED)
            t.daemon = True
            t.start()
            tlist.append(t)
        except KeyboardInterrupt:
            break
            joinAll()
        except IOError:
            break

def handle_chat(chat, outputpanel):
    global username
    while e.isSet():
        try:
            message_ar = chat.recv(1024).decode().split("___space___")
            if message_ar[0] == "___end___":
                chat_connections.remove(chat)
                chat.send(("___end______space___" + username).encode())
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

escaped_chars = {
    "13": "\n",
    "127": "",
    "8": ""
}


def handle_peer(codeshare, outputpanel,LineNum ,send=False, loaded=False):
    if send:
        current = outputpanel.get(1.0, END).strip() or "___null___"
        codeshare.send(current.encode())
    elif not loaded:
        code = codeshare.recv(1024).decode()
        print("loading code from peers")
        if code != "___null___":
            outputpanel.insert(1.0, code)

    while e.isSet():
        try:
            input_text = codeshare.recv(1024).decode().split()

            if not input_text:
                break

            if len(input_text) < 2:
                continue

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
    global username
    global peer_connections
    global chat_connections
    global notif_socket

    for conn in peer_connections:
        conn.send("___end___".encode())
        # conn.close()

    for conn in chat_connections:
        conn.send(("___end______space___" + username).encode())
        # conn.close()

    for addr in notif_peers:
        notif_socket.sendto("___end___".encode(), addr)
        # conn.close()

def close_connections():
    global peer_connections
    disconnect_peers()
    clientSocket.send("___end___".encode())
    clientSocket.close()


def handle_close():
    global root
    global is_host
    e.clear()
    root.destroy()
    close_connections()
    if is_host:
        stop_server()
    joinAll()
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
    global notif_peers
    global already_connected
    global loaded
    global notif_socket
    if not already_connected:
        try:
            for peer in peers_list:
                server = peer.split(",")[0]
                peer_port = int(peer.split(",")[1])
                notif_port = int(peer.split(",")[2])
                peer_socket = socket(AF_INET,SOCK_STREAM)
                peer_socket.connect((server,peer_port))
                peer_socket.send("___peer___".encode())

                top.OutputTextbox.configure(state=NORMAL)
                top.OutputTextbox.insert(END, "Connected to peer: " + server + "\n")
                top.OutputTextbox.configure(state=DISABLED)

                t = threading.Thread(target=handle_peer, args=(peer_socket, top.EditorTextbox, top.LineNum, False, loaded))
                t.daemon = True

                t.start()
                tlist.append(t)

                chat_socket = socket(AF_INET, SOCK_STREAM)
                chat_socket.connect((server,peer_port))
                chat_socket.send("___chat___".encode())

                t1 = threading.Thread(target=handle_chat, args=(chat_socket, top.ChatMessagesTextbox))
                t1.daemon = True
                t1.start()
                tlist.append(t1)

                top.ChatMessagesTextbox.configure(state=NORMAL)
                top.ChatMessagesTextbox.insert(END, "Connected to peer: " + server + "\n", "right")
                top.ChatMessagesTextbox.configure(state=DISABLED)

                peer_connections.append(peer_socket)
                chat_connections.append(chat_socket)
                notif_socket.sendto("___addr___".encode(), (server, notif_port))
                notif_peers.append((server, notif_port))
                already_connected = True
                loaded = True
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
    broadcast_notif(username + " is modifying the code at " + index)
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

def broadcast_notif(to_send):
    global notif_peers
    global notif_socket
    for addr in notif_peers:
        notif_socket.sendto(to_send.encode(), addr)


def broadcast_code(to_send):
    for conn in peer_connections:
        conn.send(to_send.encode())

def broadcast(to_send):
    global username
    for conn in chat_connections:
        # TODO: change hostname by username
        message = username + "___space___" + to_send
        conn.send(message.encode())

def run_code_wrapper(code, outputLabel, language):
    t = threading.Thread(target=run_code, args=(code, outputLabel, language))
    t.daemon = True
    t.start()
    tlist.append(t)

def run_code(c, outputLabel, language):
    code = c.get(1.0, END)
    broadcast_notif(username + " is executing the code")
    if code.strip() and code:
        clientSocket.send(language.encode())
        host, port =clientSocket.recv(1024).decode().split()
        code_socket = socket(AF_INET, SOCK_STREAM)
        #to reuse socket faster. It has very little consequence for ftp client.
        code_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        code_socket.connect((host, int(port)))
        i = 0
        while True:
            data = code[i*1024:(i+1)*1024]
            i+=1
            if (not data or data == '' or len(data) <= 0):
                break
            else:
                code_socket.send(data.encode())

        code_socket.send("___EOF___".encode())
        output=""
        while True:
            data = code_socket.recv(1024).decode()
            print("message" + data)
            if (data[-9:] == "___EOF___" or not data or data == '' or len(data) <= 0):
                output +=data[0:-9]
                break
            else:
                output +=data
        code_socket.close()
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
        broadcast_notif("___sent___")

def clear_output(textbox):
    textbox.configure(state=NORMAL)
    textbox.delete("1.0",END)
    textbox.configure(state=DISABLED)

last_open_dir=""
def load_file(code_textbox,linenum,langbox):
    global last_open_dir
    broadcast_notif(username + " is opening a file.")

    if langbox.get() == "Haskell":
        types = (("Haskell files", "*.hs"),("Python files", "*.py"),("All files", "*.*") )
    else:
        types= (("Python files", "*.py"),("Haskell files", "*.hs"),("All files", "*.*") )

    if last_open_dir =="":
        fname = FileDialog.askopenfilename(filetypes=types)
    else:
        fname = FileDialog.askopenfilename(filetypes=types, initialdir=last_open_dir)
    if fname:
        text = ""
        try:
            f = open(fname,"r")
            while True:
                data = f.read()
                if (not data or data == '' or len(data) <= 0):
                    f.close()
                    directory_arr = fname.split("/")
                    last_open_dir = "/".join(directory_arr[0:-1])
                    broadcast_notif(username + " opened " + directory_arr[-1])
                    break
                text+=data
            code_textbox.delete(1.0,END)
            code_textbox.insert(END,text)
            linenum.redraw()
            if(fname[-3:]==".hs"):
                lang = "Haskell"
                langbox.current(2)
            else:
                lang="Python"
                langbox.current(1)
            syntax_highlight(lang,code_textbox)
        except:
            code_textbox.delete(1.0,END)
            code_textbox.insert(END,"Unable to open file. Press CTRL-Z to undo and return to previous state")
        return
last_file_name = ""
last_file_dir = ""
def save_file(code_textbox,lang):
    global last_file_name
    global last_file_dir
    if lang == "Haskell":
        types = (("Haskell files", "*.hs"),("Python files", "*.py"),("All files", "*.*") )
    else:
        types= (("Python files", "*.py"),("Haskell files", "*.hs"),("All files", "*.*") )
    if last_file_dir == "":
        fname = FileDialog.asksaveasfilename(filetypes=types,initialfile=last_file_name)
    else:
        fname = FileDialog.asksaveasfilename(filetypes=types,initialfile=last_file_name,initialdir=last_file_dir)

    if fname:
        text = ""
        try:
            f = open(fname,"w")
            f.write(code_textbox.get(1.0,END))
            f.close()
            directory_arr = fname.split("/")
            last_file_name = directory_arr[-1]
            last_file_dir = "/".join(directory_arr[0:-1])
        except:
            print("Problem saving file")
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



        global room_name
        self.RoomLabel = Entry(top)
        self.RoomLabel.configure(background="#d9d9d9", bd=0, highlightthickness=0)
        self.RoomLabel.place(relx=0.60, rely=0.02, height=26, width=120)
        self.RoomLabel.insert(END, "Room: " )
        createToolTip(self.RoomLabel, "Share this name to code with others.")


        self.NotificationsLabel = Label(top)
        self.NotificationsLabel.place(relx=0.01, rely=0.945, height=28, width=600)
        self.NotificationsLabel.configure(anchor=W)
        self.NotificationsLabel.configure(justify=LEFT)
        self.NotificationsLabel.configure(text="""Notifications:  """)
        self.NotificationsLabel.configure(width=100)

        self.notif_text = Text(self.NotificationsLabel)
        self.notif_text.place(x=88,rely=0.7, anchor="w",height=28, width=500)
        self.notif_text.configure(width=300)
        self.notif_text.configure(background="#d9d9d9")
        self.notif_text.configure(state=DISABLED)
        self.notif_text.configure(borderwidth="0")



        self.EditorTextbox = ScrolledText(top)
        self.EditorTextbox.configure()
        self.EditorTextbox.place(relx=0.0, rely=0.07, relheight=0.87
                , relwidth=0.52)
        self.EditorTextbox.configure(background="white")
        self.EditorTextbox.configure(font="TkTextFont")
        self.EditorTextbox.configure(insertborderwidth="3")
        self.EditorTextbox.configure(selectbackground="#c4c4c4")
        self.EditorTextbox.configure(takefocus="0")
        self.EditorTextbox.configure(tabs=tkfont.Font(font=self.EditorTextbox['font']).measure(" "*4))
        self.EditorTextbox.configure(undo="1")
        self.EditorTextbox.configure(width=10)
        self.EditorTextbox.configure(wrap=NONE)
        self.EditorTextbox.configure(padx="30",pady="1.5")
        self.LineNum = TextLineNumbers(self.EditorTextbox)
        self.LineNum.attach(self.EditorTextbox)
        self.LineNum.redraw()
        self.LineNum.place(x=-30, y=-1.5, relheight=1.1, width=30)
        self.EditorTextbox.bind("<Key>", lambda e: handle_keyboard(e,self.LineNum))
        self.EditorTextbox.bind("<MouseWheel>",self.LineNum.redraw)
        self.EditorTextbox.bind("<Button-4>", self.LineNum.redraw)
        self.EditorTextbox.bind("<Button-5>", self.LineNum.redraw)
        #self.EditorTextbox.bind("<KeyRelease>",lambda e: syntax_highlight(display_support.combobox,self.EditorTextbox))
        # self.EditorTextbox.tag_configure("Token.Keyword", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Keyword.Constant", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Keyword.Declaration", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Keyword.Namespace", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Keyword.Pseudo", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Keyword.Reserved", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Keyword.Type", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Name.Class", foreground="#003D99")
        # self.EditorTextbox.tag_configure("Token.Name.Exception", foreground="#003D99")
        # self.EditorTextbox.tag_configure("Token.Name.Function", foreground="#003D99")
        # self.EditorTextbox.tag_configure("Token.Operator.Word", foreground="#660029")
        # self.EditorTextbox.tag_configure("Token.Comment.Multi", foreground="#3d3d3d")
        # self.EditorTextbox.tag_configure("Token.Comment.Single", foreground="#3d3d3d")
        # self.EditorTextbox.tag_configure("Token.Literal.String", foreground="#248F24")

        # The following is the list of styles that can be used
        #['manni', 'igor', 'lovelace', 'xcode', 'vim', 'autumn', 'abap', 'vs', 'rrt',
        #'native', 'perldoc', 'borland', 'arduino', 'tango', 'emacs', 'friendly',
        #'monokai', 'paraiso-dark', 'colorful', 'murphy', 'bw', 'pastie', 'rainbow_dash',
        #'algol_nu', 'paraiso-light', 'trac', 'default', 'algol', 'fruity']
        try:
            self.EditorTextbox.configure(yscrollcommand=(lambda fir,las: autoscrollLine(self.EditorTextbox.vsb, self.LineNum,fir,las)))
        except Exception as e:
            print (e)
            pass
        style = get_style_by_name('default')

        for token, predefined in style:
            if predefined['color']:
                color = "#" + predefined['color']
            else:
                color = None
            self.EditorTextbox.tag_configure(str(token), foreground=color)


        self.LanguageSelect = ttk.Combobox(top)
        self.LanguageSelect.place(relx=0.34, rely=0.02, relheight=0.03
                , relwidth=0.23)
        self.value_list = ["python2","python3","Haskell"]
        self.LanguageSelect.configure(values=self.value_list)
        self.LanguageSelect.configure(textvariable=display_support.combobox)
        self.LanguageSelect.configure(takefocus="")
        self.LanguageSelect.current(1)
        createToolTip(self.LanguageSelect, "Select your language.")

        self.RunButton = Button(top)
        self.RunButton.place(relx=0.79, rely=0.01, height=26, width=50)
        self.RunButton.configure(activebackground="#d9d9d9")
        self.RunButton.configure(command=(lambda : run_code_wrapper(self.EditorTextbox, self.OutputTextbox,display_support.combobox)))
        self.RunButton.configure(text="""Run""")
        top.bind("<F5>",(lambda x : run_code_wrapper(self.EditorTextbox, self.OutputTextbox,self.LanguageSelect.get())))
        createToolTip(self.RunButton, "Press F5 to run.")

        def langselection(e):
            display_support.combobox = self.LanguageSelect.get()

        self.LanguageSelect.bind("<<ComboboxSelected>>", langselection)

        self.LanguageStyle = ttk.Combobox(top)
        self.LanguageStyle.place(relx=0.10, rely=0.02, relheight=0.03
                , relwidth=0.23)
        self.LanguageStyle.configure(values=['manni', 'igor', 'lovelace', 'xcode', 'vim', 'autumn', 'abap', 'vs', 'rrt',
        'native', 'perldoc', 'borland', 'arduino', 'tango', 'emacs', 'friendly',
        'monokai', 'paraiso-dark', 'colorful', 'murphy', 'bw', 'pastie', 'rainbow_dash',
        'algol_nu', 'paraiso-light', 'trac', 'default', 'algol', 'fruity'])
        self.LanguageStyle.configure(textvariable=style)
        self.LanguageStyle.configure(takefocus="")
        self.LanguageStyle.current(26)
        createToolTip(self.LanguageStyle, "Select your style.")

        self.LanguageStyle.bind("<<ComboboxSelected>>", lambda e : change_style(self.LanguageStyle.get(),display_support.combobox, self.EditorTextbox))

        self.OutputTextbox = ScrolledText(top)
        self.OutputTextbox.place(relx=0.52, rely=0.07, relheight=0.52
                , relwidth=0.48)
        self.OutputTextbox.configure(background="white")
        self.OutputTextbox.configure(font="TkTextFont")
        self.OutputTextbox.configure(insertborderwidth="3")
        self.OutputTextbox.configure(selectbackground="#c4c4c4")
        self.OutputTextbox.configure(undo="1")
        self.OutputTextbox.configure(width=10)
        self.OutputTextbox.configure(wrap=CHAR)
        self.OutputTextbox.insert(END, '''Output will show up here\n''')
        self.OutputTextbox.configure(state=DISABLED)

        self.ChatMessagesTextbox = ScrolledText(top)
        self.ChatMessagesTextbox.place(relx=0.52, rely=0.63, relheight=0.26
                , relwidth=0.48)
        self.ChatMessagesTextbox.configure(background="white")
        self.ChatMessagesTextbox.configure(font="TkTextFont")
        self.ChatMessagesTextbox.configure(insertborderwidth="3")
        self.ChatMessagesTextbox.configure(selectbackground="#c4c4c4")
        self.ChatMessagesTextbox.configure(undo="1")
        self.ChatMessagesTextbox.configure(width=10)
        self.ChatMessagesTextbox.configure(wrap=WORD)
        self.ChatMessagesTextbox.tag_configure("right", justify="right")
        self.ChatMessagesTextbox.tag_configure("left", justify="left")
        self.ChatMessagesTextbox.configure(state=DISABLED)

        self.SendButton = Button(top)
        self.SendButton.place(relx=0.92, rely=0.89, relheight=0.05, relwidth=.08)
        self.SendButton.configure(activebackground="#d9d9d9")
        self.SendButton.configure(text='''Send''')
        self.SendButton.configure(command=(lambda: send_message(self.ChatEntry,self.ChatMessagesTextbox)))

        self.ChatEntry = Entry(top)
        self.ChatEntry.place(relx=0.52, rely=0.89, relheight=0.05, relwidth=0.4)
        self.ChatEntry.configure(background="white")
        self.ChatEntry.configure(font="TkFixedFont")
        self.ChatEntry.configure(width=306)
        self.ChatEntry.bind("<KeyPress>", (lambda x: broadcast_notif(username + " is typing...")))
        self.ChatEntry.bind("<Key-Return>", (lambda x: send_message(self.ChatEntry,self.ChatMessagesTextbox)))
        self.ChatEntry.bind("<Key-KP_Enter>", (lambda x: send_message(self.ChatEntry,self.ChatMessagesTextbox)))
        self.ChatEntry.bind("<Key-Insert>", (lambda x: send_message(self.ChatEntry,self.ChatMessagesTextbox)))

        top.bind("<Control-Left>", lambda x: self.EditorTextbox.focus_set())
        top.bind("<Control-Right>", lambda x: self.ChatEntry.focus_set())

        self.ChatLabel = Label(top)
        self.ChatLabel.place(relx=0.52, rely=0.595, height=18, width=99)
        self.ChatLabel.configure(text='''Chat with peers''')

        self.ClearButton = Button(top)
        self.ClearButton.place(relx=0.79, rely=0.595, height=18, width=50)
        self.ClearButton.configure(activebackground="#d9d9d9")
        self.ClearButton.configure(command=(lambda : clear_output(self.OutputTextbox)))
        self.ClearButton.configure(text="""Clear""")
        top.bind("<Control-l>", lambda x : clear_output(self.OutputTextbox))
        # self.NotificationsLabel = Label(top)
        # self.NotificationsLabel.place(relx=0.70, rely=0.595, height=18, width=99)
        # self.NotificationsLabel.configure(text='''Notifications''')

        self.OpenButton = Button(top)
        self.OpenButton.place(relx=00, rely=0.01, relheight=0.05, relwidth=.08)
        self.OpenButton.configure(activebackground="#d9d9d9")
        self.OpenButton.configure(text='''Open''')
        self.OpenButton.configure(command=(lambda: load_file(self.EditorTextbox, self.LineNum,self.LanguageSelect)))
        createToolTip(self.OpenButton, "Open a file.")
        top.bind("<Control-o>", lambda x: load_file(self.EditorTextbox, self.LineNum,self.LanguageSelect))

        self.SaveButton = Button(top)
        self.SaveButton.place(relx=.92, rely=0.01, relheight=0.05, relwidth=.08)
        self.SaveButton.configure(activebackground="#d9d9d9")
        self.SaveButton.configure(text='''Save''')
        self.SaveButton.configure(command=(lambda:  save_file(self.EditorTextbox, self.LanguageSelect.get())))
        createToolTip(self.SaveButton, "Save your code to a file.")
        top.bind("<Control-s>", lambda x: save_file(self.EditorTextbox, self.LanguageSelect.get()))


        self.OverlayRoomPick = Message(top)
        self.OverlayRoomPick.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=1.0)
        self.OverlayRoomPick.configure(anchor=N)
        self.OverlayRoomPick.configure(font=font9)
        self.OverlayRoomPick.configure(pady="10")
        self.OverlayRoomPick.configure(text='''Join a coding room''')
        self.OverlayRoomPick.configure(width=773)

        self.OverlayRoomLabel = Label(self.OverlayRoomPick)
        self.OverlayRoomLabel.place(relx=0.37, rely=0.20, height=28, width=50)
        self.OverlayRoomLabel.configure(activebackground="#f9f9f9")
        self.OverlayRoomLabel.configure(text='''Room #''')

        self.OverlayJoinRoomLabel = Label(self.OverlayRoomPick)
        self.OverlayJoinRoomLabel.place(relx=0.38, rely=0.15, height=28, width=206)
        self.OverlayJoinRoomLabel.configure(activebackground="#f9f9f9")
        self.OverlayJoinRoomLabel.configure(font=font11)
        self.OverlayJoinRoomLabel.configure(text='''Join an existing room''')

        self.OverlayRoomEntry = Entry(self.OverlayRoomPick)
        self.OverlayRoomEntry.place(relx=0.42, rely=0.20, relheight=0.05, relwidth=0.25)
        self.OverlayRoomEntry.configure(background="white")
        self.OverlayRoomEntry.configure(font="TkFixedFont")
        self.OverlayRoomEntry.configure(width=306)

        self.OverlayJoinButton = Button(self.OverlayRoomPick)
        self.OverlayJoinButton.place(relx=0.47, rely=0.25, height=26, width=65)
        self.OverlayJoinButton.configure(activebackground="#d9d9d9")
        self.OverlayJoinButton.configure(text='''Join''')
        self.OverlayJoinButton.configure(command=(lambda : join_room(self.OverlayRoomEntry.get(), self.OverlayRoomPick, self, self.RoomLabel)))


        self.OverlayCreateLabel = Label(self.OverlayRoomPick)
        self.OverlayCreateLabel.place(relx=0.38, rely=0.33, height=28, width=206)
        self.OverlayCreateLabel.configure(activebackground="#f9f9f9")
        self.OverlayCreateLabel.configure(font=font11)
        self.OverlayCreateLabel.configure(text='''Create a new room''')

        self.OverlayCreateButton = Button(self.OverlayRoomPick)
        self.OverlayCreateButton.place(relx=0.47, rely=0.42, height=26, width=65)
        self.OverlayCreateButton.configure(activebackground="#d9d9d9")
        self.OverlayCreateButton.configure(text='''Create''')
        self.OverlayCreateButton.configure(command=(lambda: create_room(self.OverlayRoomPick, self, self.RoomLabel)))




# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    """Configure the scrollbars for a widget."""

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            self.vsb = ttk.Scrollbar(master, orient="vertical", command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient="horizontal", command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(self.vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky="nsew")
        try:
            self.vsb.grid(column=1, row=0, sticky="ns")
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

def autoscrollLine(sbar,LineNum, first, last):
    LineNum.redraw()
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)

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


######Taken and edited from from http://stackoverflow.com/a/16375233
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
            self.create_text(2,y,anchor="nw",font=self.textwidget['font'], text=linenum,fill="#ff4c4c")
            i = self.textwidget.index("%s+1line" % i)

if __name__ == "__main__":
    vp_start_gui()
