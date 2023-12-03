from tkinter import Tk
from game2048 import event_handler
from config import OFFSET
import tkinter


if __name__ == '__main__':

    gwind = Tk()
    gwind.title("2048")
    gwind.configure(width=404, height=404 + OFFSET, pady=0, padx=0)

    event_handler = event_handler(gwind)

    # newmenu = tkinter.Menu(gwind)
    #
    # menu1 = tkinter.Menu(newmenu, tearoff=False)
    # menu1.add_command(label="HELP", command= lambda : print("HELP"))
    # menu1.add_separator()
    #
    # newmenu.add_cascade(label= "HELPP", menu = menu1)
    #
    # gwind.config(menu=newmenu)

    # gwind.overrideredirect(True)

    gwind.tkraise()

    gwind.mainloop()
