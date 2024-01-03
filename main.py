from tkinter import Tk
from game2048 import event_handler
from config import OFFSET
import tkinter


if __name__ == '__main__':

    gwind = Tk()
    gwind.title("2048")
    gwind.configure(width=404, height=404 + OFFSET, pady=0, padx=0)

    event_handler = event_handler(gwind)

    mainMenu = tkinter.Menu(gwind)

    optionsMenu = tkinter.Menu(mainMenu, tearoff=False)
    mainMenu.add_cascade(label="Options", menu=optionsMenu)

    optionsMenu.add_command(label="Restart", command=event_handler.hard_reset)
    optionsMenu.add_separator()
    optionsMenu.add_command(label="Exit", command=gwind.destroy)

    gwind.config(menu=mainMenu)

    gwind.tkraise()

    gwind.mainloop()
