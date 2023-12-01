from tkinter import *
from event_handler import event_handler
from event_handler import OFFSET

if __name__ == '__main__':
    gwind = Tk()
    gwind.title("2048")
    gwind.configure(width=404, height=404 + OFFSET, pady=0, padx=0)

    event_handler = event_handler(gwind)


    def make_move(event):
        binds = {"a": "left", "d": "right", "w": "up", "s": "down"}
        key = event.keysym.lower()
        if key in binds.keys():
            direction = binds[key][:1]
            event_handler.make_move(direction)
        elif key in binds.values():
            direction = key[:1]
            event_handler.make_move(direction)
        else:
            return False


    gwind.bind("<Key>", make_move)

    gwind.mainloop()
