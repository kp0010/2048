import random
import time
import tkinter
import tkinter.ttk
from threading import Thread

from node import node, EMPTY_COLOR, INITIAL_NODES, OFFSET

ANIMATION_SPEED = 0.000001
STEP_SIZE = 2


# TODO : {Show game over on screen} Done
# TODO : Add a new Reset Button
# TODO : Store High Score
# TODO : Use the self.moveanimating boolean to check if move is available or not to do


def make_empty(enode: node):
    enode.value = 0
    enode.itemconfig(enode.num, text="")
    enode.config(bg=EMPTY_COLOR)


class event_handler:
    def __init__(self, window):
        self.score = 0
        self.window = window
        self.move_animating = False
        self.canvasmain = tkinter.Canvas(width=404, height=404)
        self.canvasmain.place(x=0, y=OFFSET)
        self.drawlines()
        self.nodes = [[node(x=i, y=j, empty=True) for i in range(4)] for j in range(4)]

        self.scoretext = tkinter.Label(text=f"Score : {self.score}", font=("ariel", 10, "bold"))
        self.scoretext.place(x=10, y=5)

        for i in range(INITIAL_NODES):
            self.choose_rand_available()

        window.bind("<Key>", self.move_handler)

    def move_handler(self, event):
        if not self.move_animating:
            binds = {"a": "left", "d": "right", "w": "up", "s": "down"}
            key = event.keysym.lower()
            if key in binds.keys():
                direction = binds[key][:1]
                self.make_move(direction)
            elif key in binds.values():
                direction = key[:1]
                self.make_move(direction)
            else:
                return False

    def drawlines(self):
        for i in range(1, 4):
            self.canvasmain.create_line(101 * i, 0, 101 * i, 404)  # VERT
            self.canvasmain.create_line(0, (101 * i), 404, (101 * i))  # HOR
        self.canvasmain.create_line(0, 1, 404, 1)

    def choose_rand_available(self):
        visited = []
        while True:
            i, j = random.randint(0, 3), random.randint(0, 3)
            current = self.nodes[j][i]
            if not current.value and (i, j) not in visited:
                current.increment_val()
                if random.randint(0, 10) == 5:
                    current.increment_val()
                return True
            else:
                if (i, j) not in visited:
                    visited.append((i, j))
                if len(visited) == 16:
                    return False

    def check_valid_move(self, direction):
        dirc = direction
        dir_ranges = {"d": ((0, 3), (0, 4)), "u": [(1, 4), (0, 4)], "l": ((0, 4), (1, 4)), "r": ((0, 4), (0, 3))}
        dir_add = {"d": (1, 0), "u": (-1, 0), "l": (0, -1), "r": (0, 1)}
        icur, jcur = dir_ranges[dirc]
        iadd, jadd = dir_add[dirc]
        for i in range(*icur):
            for j in range(*jcur):
                current = self.nodes[i][j]
                firstshftflag = True

                if not current.value:
                    continue

                # right
                if iadd > 0:
                    for k in range(i + 1, 4):
                        shifted = self.nodes[k][j]
                        if not shifted.value:
                            return True
                        if firstshftflag and (current.value == shifted.value):
                            return True
                        firstshftflag = False

                # left
                if iadd < 0:
                    for k in range(i - 1, -1, -1):
                        shifted = self.nodes[k][j]
                        if not shifted.value:
                            return True
                        if firstshftflag and (current.value == shifted.value):
                            return True
                        firstshftflag = False
                # down
                if jadd > 0:
                    for k in range(j + 1, 4):
                        shifted = self.nodes[i][k]
                        if not shifted.value:
                            return True
                        if firstshftflag and (current.value == shifted.value):
                            return True
                        firstshftflag = False
                # up
                if jadd < 0:
                    for k in range(j - 1, -1, -1):
                        shifted = self.nodes[i][k]
                        if not shifted.value:
                            return True
                        if firstshftflag and (current.value == shifted.value):
                            return True
                        firstshftflag = False

        return False

    def make_move(self, direction):

        if not self.check_valid_move(direction):
            if not self.check_all_moves():
                self.scoretext.config(text=f"GAME OVER!  FINAL SCORE : {self.score}")
                return False
            return False

        self.move_animating = True

        if direction == "r":
            self.move_right()
        elif direction == "l":
            self.move_left()
        elif direction == "d":
            self.move_down()
        elif direction == "u":
            self.move_up()

        self.move_animating = False

        self.choose_rand_available()

    def __clear_flags(self):
        for row in self.nodes:
            for el in row:
                el.changed_curr_pass = False

    def move_right(self):
        self.__clear_flags()

        for i in range(2, -1, -1):
            for j in range(0, 4):
                k = 1
                current = self.nodes[j][i]

                if current.value == 0:
                    continue

                shifted = self.nodes[j][i + k]
                while not shifted.value:
                    k += 1
                    if (i + k) < 4:
                        shifted = self.nodes[j][i + k]
                    else:
                        break

                # merge
                if shifted.value == current.value:
                    finalpos = self.nodes[j][i + k]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j][i + k - 1]
                        Thread(target=self.moveanimate, args=(current, finalpos)).run()
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)
                # shift
                else:
                    finalpos = self.nodes[j][i + k - 1]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if current.pos != finalpos.pos:
                        while current.value > finalpos.value:
                            finalpos.increment_val()
                        make_empty(current)

    def move_left(self):
        self.__clear_flags()

        for i in range(1, 4):
            for j in range(0, 4):
                k = 1
                current = self.nodes[j][i]

                if current.value == 0:
                    continue

                shifted = self.nodes[j][i - k]
                while not shifted.value:
                    k += 1
                    if (i - k) >= 0:
                        shifted = self.nodes[j][i - k]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = self.nodes[j][i - k]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j][i - k + 1]
                        Thread(target=self.moveanimate, args=(current, finalpos)).run()
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)

                else:
                    finalpos = self.nodes[j][i - k + 1]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if current.pos != finalpos.pos:
                        while current.value > finalpos.value:
                            finalpos.increment_val()
                        make_empty(current)

    def move_down(self):
        self.__clear_flags()

        for j in range(2, -1, -1):
            for i in range(0, 4):
                k = 1
                current = self.nodes[j][i]

                if current.value == 0:
                    continue

                shifted = self.nodes[j + k][i]
                while not shifted.value:
                    k += 1
                    if (j + k) <= 3:
                        shifted = self.nodes[j + k][i]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = self.nodes[j + k][i]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j + k - 1][i]
                        Thread(target=self.moveanimate, args=(current, finalpos)).run()
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)

                else:
                    finalpos = self.nodes[j + k - 1][i]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if current.pos != finalpos.pos:
                        while current.value > finalpos.value:
                            finalpos.increment_val()
                        make_empty(current)

    def move_up(self):
        self.__clear_flags()

        for j in range(1, 4):
            for i in range(0, 4):
                k = 1
                current = self.nodes[j][i]

                if current.value == 0:
                    continue

                shifted = self.nodes[j - k][i]
                while not shifted.value:
                    k += 1
                    if (j - k) >= 0:
                        shifted = self.nodes[j - k][i]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = self.nodes[j - k][i]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j - k + 1][i]
                        Thread(target=self.moveanimate, args=(current, finalpos)).run()
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)

                else:
                    finalpos = self.nodes[j - k + 1][i]
                    Thread(target=self.moveanimate, args=(current, finalpos)).run()
                    if current.pos != finalpos.pos:
                        while current.value > finalpos.value:
                            finalpos.increment_val()
                        make_empty(current)

    def check_all_moves(self):
        u, d = self.check_valid_move("u"), self.check_valid_move("d")
        l, r = self.check_valid_move("l"), self.check_valid_move("r")
        return u or d or l or r

    def moveanimate(self, startpos: node, endpos: node):
        startx, starty = (i * 101 for i in startpos.pos)
        endx, endy = (i * 101 for i in endpos.pos)
        ix, iy = startx, starty
        tkinter.Misc.lift(startpos)

        if startx != endx:
            # shift hor + (100 if startx < endx else -100)
            while ix != endx:
                time.sleep(ANIMATION_SPEED)
                # if startx < endx then add or else subtract
                ix = ix + (STEP_SIZE if startx <= endx else -STEP_SIZE)
                if (startx < endx < ix) or (startx > endx > ix):
                    startpos.place(x=endx, y=endy + OFFSET)
                    break
                startpos.place(x=ix + 1, y=endy + OFFSET + 1)
                self.window.update()
        else:
            # shift vert + (100 if starty < endy else -100)
            while iy != endy:
                time.sleep(ANIMATION_SPEED)
                # if startx < endx then add or else subtract
                iy = iy + (STEP_SIZE if starty <= endy else -STEP_SIZE)
                if (starty < endy < iy) or (starty > endy > iy):
                    startpos.place(x=endx, y=endy + OFFSET)
                    break
                startpos.place(x=startx + 1, y=iy + OFFSET + 1)
                self.window.update()

        startpos.place(x=startx + 1, y=starty + OFFSET + 1)
