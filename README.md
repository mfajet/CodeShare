# CodeShare

## About this project
A code sharing application. Creating this as a school project.
It includes the following features:
* code synchronization with peers
* Chatting with peers
* Notifications on what peers are doing
* Open files
* Save files
* Execute code
* Syntax highlighting with styles you can choose from
* Rooms that you can create and join to be with peers

The frontend was created with tkinter and ttk by using PAGE (Python Automatic GUI Generator) initially which can be found at http://page.sourceforge.net/
After that, the frontend was done using tkinter without bothering with PAGE

## Being able to run it
In order to run the project, make sure to have the following installed
* Python
* tkinter (sudo apt-get install python3-tk)
* ttk (included in tkinter if using python3)
* pygments (sudo apt-get install python3-pygments)
* ghci (sudo apt-get install haskell-platform)
The haskell platform is only necessary if you want to run haskell code.



The server can be started by doing the following:
```
python3 server.py
```
The application can be run by doing the following:
```
python3 mydisplay.py
```

## How to use it

For a thorough testing of the application, you will want to open up multiple application windows.
Code sharing will take place whenever two clients join the same room.
To do so, one client clicks the "create room" button. Afterwards, they share the generated room number with anybody they want to code with. The people who receive the code put it in the join room box and hit enter.
From then on, the people in the room can code together and have synchronized code; they can chat with each other; They can run code (which takes place on the server so that clients don't need to worry about having the right packages installed); they can open and save files; They can choose their language; they can choose the theme for the syntax highlighting; They can see who is currently typing or doing some other action.

For an enhanced experience, there are helpful key bindings.
* ctrl-a: select all
* ctrl-left arrow: focus on editor text box
* ctrl-right arrow: focus on chat text box
* ctrl-o: open files
* ctrl-s: save file
* ctrl-l: clear output
* F5: Run code
* F11: Toggle fullscreen
* enter: In the chat entry or join room entry, pressing enter will send the message or join room without needing to click the button

The room name you're in can always be found in the top of the application window.

An interesting thing to note is that it doesn't matter how long the code you write is, it'll run it all. The output is slightly different however. The output is limited, not by how long the output is, but how long the program takes to produce its output. This was a design choice in order to serve as a basic measure of security. On one hand, since everyone runs their code on the server rather than locally (a design choice made so that clients don't need to deal with installation), allowing people to run very long, resource intensive programs would put a lot of strain on the server even if they aren't attempting to be malicious. On the other hand, one could write a simple program that loops forever which would very clearly cause problems for the server. For these reasons, program execution is limited to programs that terminate in less than 10 seconds. In the future, this number could be easily changed if it was felt that the time limit should be extended.

To test out this security measure, one can type in the editor:
```
while True:
    print("If this runs forever, your server sucks.")
```
Click run or press F5 and you will see the response "Execution canceled. Process took too long." as long as the language is set to python 2 or 3. (Otherwise it simply isn't valid code and will produce an error message).


To open a file, click open or press ctrl-o, you can select any file from your file system.
If your language is currently Haskell, it'll only show Haskell files, but you can tell it to show python files or all files. The same applies to if your language is python.
If your language is python and you open a Haskell file, it will change your language to Haskell.
If you select a file that is in none of the available languages, that is not a problem we handle other than by telling you the error message when trying to run it.
If you open a file in a certain directory, we believe it's likely that you'll open a file in that same directory or a nearby directory later so it remembers the directory where you opened that file in.

If you wish to save the code you wrote inside of a file, you can press save or click ctrl-s.
If you save a file once, it remembers the directory and name where you saved it so that you can easily save it the next time.

As you type your code, you'll notice that it'll style the code for you. This syntax highlighting can be controlled to a certain extent by using the drop down menu in order to select your style.

If you wish to change your language, there is a dropdown for that as well.

If you're unsure of what something does, mouse over it to check if it has a tooltip

To send messages to the people in your room, simply type it in the entry in the bottom right and click send or press enter.
