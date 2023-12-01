import colorsys
import random
import time
import tkinter
import tkinter.ttk
from node import node

MAX_VALUE = 10
EMPTY_COLOR = "#F7F7F7"
INITIAL_NODES = 2
OFFSET = 30


# TODO : {Show game over on screen} Done
# TODO : Add a new Reset Button
# TODO : Store High Score

def make_empty(enode: node):
    enode.value = 0
    enode.itemconfig(enode.num, text="")
    enode.config(bg=EMPTY_COLOR)


def calc_color(value):
    hex_color = "#00ff9c"
    factor = 0

    while value > 1:
        factor += 1
        value /= 2

    saturation_factor = factor / MAX_VALUE

    rgb_color_raw = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

    # Convert RGB to HSV
    hsv_color_r = colorsys.rgb_to_hsv(rgb_color_raw[0] / 255.0, rgb_color_raw[1] / 255.0, rgb_color_raw[2] / 255.0)

    # Adjust saturation
    new_saturation = min(1.0, max(0.0, hsv_color_r[1] * saturation_factor) * 2)
    hsv_color = (hsv_color_r[0], new_saturation, hsv_color_r[2])

    rgb_color = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(*hsv_color))

    # Convert RGB to hex
    new_hex_color = "#{:02x}{:02x}{:02x}".format(rgb_color[0], min(255, rgb_color[1] + 70), min(255, rgb_color[2] + 70))

    return new_hex_color


class event_handler:
    def __init__(self, window):
        self.score = 0
        self.window = window
        self.canvasmain = tkinter.Canvas(width=404, height=404)
        self.canvasmain.place(x=0, y=OFFSET)
        self.drawlines()
        self.nodes = [[node(x=i, y=j, empty=True) for i in range(4)] for j in range(4)]

        self.scoretext = tkinter.Label(text=f"Score : {self.score}", font=("ariel", 10, "bold"))
        self.scoretext.place(x=10, y=5)

        for i in range(INITIAL_NODES):
            self.choose_rand_available()
    
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
                    print("All Nodes Visited")
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
                self.scoretext.config(text=f"GAME OVER! FINAL SCORE : {self.score}")
                print(f"GAME OVER \nScore : {self.score}")
                return False
            return False

        if direction == "r":
            self.move_right()
        elif direction == "l":
            self.move_left()
        elif direction == "d":
            self.move_down()
        elif direction == "u":
            self.move_up()

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
                    self.moveanimate(current, finalpos)
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j][i + k - 1]
                        self.moveanimate(current, finalpos)
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)
                # shift
                else:
                    finalpos = self.nodes[j][i + k - 1]
                    self.moveanimate(current, finalpos)
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
                    self.moveanimate(current, finalpos)
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j][i - k + 1]
                        self.moveanimate(current, finalpos)
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)

                else:
                    finalpos = self.nodes[j][i - k + 1]
                    self.moveanimate(current, finalpos)
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
                    self.moveanimate(current, finalpos)
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j + k - 1][i]
                        self.moveanimate(current, finalpos)
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)

                else:
                    finalpos = self.nodes[j + k - 1][i]
                    self.moveanimate(current, finalpos)
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
                    self.moveanimate(current, finalpos)
                    if not finalpos.changed_curr_pass:
                        finalpos.changed_curr_pass = True
                        current.changed_curr_pass = False
                        self.score += finalpos.increment_val()
                        self.scoretext.config(text=f"Score : {self.score}")
                        make_empty(current)
                    else:
                        finalpos = self.nodes[j - k + 1][i]
                        self.moveanimate(current, finalpos)
                        if current.pos != finalpos.pos:
                            while current.value > finalpos.value:
                                finalpos.increment_val()
                            make_empty(current)

                else:
                    finalpos = self.nodes[j - k + 1][i]
                    self.moveanimate(current, finalpos)
                    if current.pos != finalpos.pos:
                        while current.value > finalpos.value:
                            finalpos.increment_val()
                        make_empty(current)

    def check_all_moves(self):
        u, d = self.check_valid_move("u"), self.check_valid_move("d")
        l, r = self.check_valid_move("l"), self.check_valid_move("r")
        return u or d or l or r

    def moveanimate(self, startpos: node, endpos: node, merge=0):
        startx, starty = startpos.pos
        startx *= 101
        starty *= 101
        endx, endy = endpos.pos
        endy *= 101
        endx *= 101
        ix, iy = startx, starty

        print(starty, startx, endx, endy)

        if startx != endx:
            # shift hor
            while ix != endx:
                time.sleep(0.000001)
                # if startx < endx then add or else subtract
                ix = ix + (1 if startx <= endx else -1)
                startpos.place(x=ix, y=endy + OFFSET)
                self.window.update()
        else:
            # shift vert
            while iy != endy:
                time.sleep(0.000001)
                # if startx < endx then add or else subtract
                iy = iy + (1 if starty <= endy else -1)
                startpos.place(x=startx, y=iy + OFFSET)
                self.window.update()

        print(startx, startx + (startx % 100), starty)

        startpos.place(x=startx + 1, y=starty + OFFSET + 1)
        self.drawlines()
