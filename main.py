from tkinter import Tk
from game2048 import event_handler, OFFSET


if __name__ == '__main__':

    gwind = Tk()
    gwind.title("2048")
    gwind.configure(width=404, height=404 + OFFSET, pady=0, padx=0)

    event_handler = event_handler(gwind)

    gwind.tkraise()

    gwind.mainloop()
