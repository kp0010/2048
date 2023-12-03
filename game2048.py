import random
import time
import tkinter
import tkinter.ttk
from threading import Thread

from node import node, EMPTY_COLOR, INITIAL_NODES, OFFSET

ANIMATION_SPEED = 0.00001
STEP_SIZE = 3


# TODO : Add a new Reset Button
# TODO : Store High Score


def make_empty(enode: node):
    enode.value = 0
    enode.itemconfig(enode.num, text="")
    enode.config(bg=EMPTY_COLOR)


class event_handler:
    def __init__(self, window):
        self.animatedThreads = []
        self.score = 0
        self.window = window
        self.move_animating = False
        self.canvasmain = tkinter.Canvas(width=404, height=404, bg=EMPTY_COLOR)
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

        if direction in ("l", "r"):
            self.move_horizontal(direction)
        elif direction in ("d", "u"):
            self.move_vertical(direction)


        def turnonanimate():
            self.move_animating = False
            self.choose_rand_available()

        turnonanimate()

        self.animatedThreads = []


    def __clear_flags(self):
        for row in self.nodes:
            for el in row:
                el.changed_curr_pass = False


    def move_vertical(self, direction):
        self.__clear_flags()

        ranges = {"d": [(2, -1, -1), (0, 4), 1], "u": [(1, 4), (0, 4), -1]}

        range1 = ranges[direction][0]
        range2 = ranges[direction][1]
        sign = ranges[direction][2]

        for j in range(*range1):
            for i in range(*range2):
                k = 1
                current = self.nodes[j][i]

                if current.value == 0:
                    continue

                shifted = self.nodes[j + (k * sign)][i]
                while not shifted.value:
                    k += 1
                    if 0 <= (j + (k * sign)) <= 3:
                        shifted = self.nodes[j + (k * sign)][i]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = self.nodes[j + (k * sign)][i]
                    if not finalpos.changed_curr_pass:
                        self.animatedThreads.append(Thread(target=self.move_animated, args=(current, finalpos, "1")))
                    else:
                        finalpos = self.nodes[j + (k * sign) - (1 * sign)][i]
                        self.animatedThreads.append(Thread(target=self.move_animated, args=(current, finalpos, "2")))

                else:
                    finalpos = self.nodes[j + (k * sign) - (1 * sign)][i]
                    self.animatedThreads.append(Thread(target=self.move_animated, args=(current, finalpos, "2")))

            try:
                for thread in self.animatedThreads:
                    thread.run()

                self.animatedThreads = []
            except AttributeError:
                pass


    def move_horizontal(self, direction):
        self.__clear_flags()

        ranges = {"r": [(2, -1, -1), (0, 4), 1], "l": [(1, 4), (0, 4), -1]}

        range1 = ranges[direction][0]
        range2 = ranges[direction][1]
        sign = ranges[direction][2]

        for i in range(*range1):
            for j in range(*range2):
                k = 1
                current = self.nodes[j][i]

                if current.value == 0:
                    continue

                shifted = self.nodes[j][i + (k * sign)]
                while not shifted.value:
                    k += 1
                    if 0 <= (i + (k * sign)) <= 3:
                        shifted = self.nodes[j][i + (k * sign)]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = self.nodes[j][i + (k * sign)]
                    if not finalpos.changed_curr_pass:
                        self.animatedThreads.append(Thread(target=self.move_animated, args=(current, finalpos, "1")))
                    else:
                        finalpos = self.nodes[j][i + (k * sign) - (1 * sign)]
                        self.animatedThreads.append(Thread(target=self.move_animated, args=(current, finalpos, "2")))

                else:
                    finalpos = self.nodes[j][i + (k * sign) - (1 * sign)]
                    self.animatedThreads.append(Thread(target=self.move_animated, args=(current, finalpos, "2")))

            try:
                for thread in self.animatedThreads:
                    thread.run()

                self.animatedThreads = []
            except AttributeError:
                pass


    def move_actual(self, current: node, finalpos: node, mode: str):

        match mode:
            case "1":
                finalpos.changed_curr_pass = True
                current.changed_curr_pass = False
                self.score += finalpos.increment_val()
                self.scoretext.config(text=f"Score : {self.score}")
                make_empty(current)
            case "2":
                if current.pos != finalpos.pos:
                    while current.value > finalpos.value:
                        finalpos.increment_val()
                    make_empty(current)


    def check_all_moves(self):
        u, d = self.check_valid_move("u"), self.check_valid_move("d")
        l, r = self.check_valid_move("l"), self.check_valid_move("r")
        return u or d or l or r

    def move_animated(self, startpos: node, endpos: node, mode: str):
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

        # Thread(target=self.move_actual, args=(startpos, endpos, mode)).run()
        self.move_actual(startpos, endpos, mode)
        startpos.place(x=startx + 1, y=starty + OFFSET + 1)
