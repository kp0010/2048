import random
import tkinter as tk
from config import *
import tkinter.messagebox as tkmessagebox
from node import node


def valid_move_checker(direction: str, nodes):
    dirc = direction
    dir_ranges = {"d": ((0, 3), (0, 4)), "u": [(1, 4), (0, 4)], "l": ((0, 4), (1, 4)), "r": ((0, 4), (0, 3))}
    dir_add = {"d": (1, 0), "u": (-1, 0), "l": (0, -1), "r": (0, 1)}
    icur, jcur = dir_ranges[dirc]
    iadd, jadd = dir_add[dirc]
    for i in range(*icur):
        for j in range(*jcur):
            current = nodes[i][j]
            firstshftflag = True

            if not current.value:
                continue

            # right
            if iadd > 0:
                for k in range(i + 1, 4):
                    shifted = nodes[k][j]
                    if not shifted.value:
                        return True
                    if firstshftflag and (current.value == shifted.value):
                        return True
                    firstshftflag = False

            # left
            if iadd < 0:
                for k in range(i - 1, -1, -1):
                    shifted = nodes[k][j]
                    if not shifted.value:
                        return True
                    if firstshftflag and (current.value == shifted.value):
                        return True
                    firstshftflag = False
            # down
            if jadd > 0:
                for k in range(j + 1, 4):
                    shifted = nodes[i][k]
                    if not shifted.value:
                        return True
                    if firstshftflag and (current.value == shifted.value):
                        return True
                    firstshftflag = False
            # up
            if jadd < 0:
                for k in range(j - 1, -1, -1):
                    shifted = nodes[i][k]
                    if not shifted.value:
                        return True
                    if firstshftflag and (current.value == shifted.value):
                        return True
                    firstshftflag = False

    return False


class event_handler:
    def __init__(self, window):
        self.score = 0
        self.window = window
        self.move_animating = False

        self.canvasmain = tk.Canvas(width=404, height=404, bg=EMPTY_COLOR)
        self.canvasmain.place(x=0, y=OFFSET)

        self.nodes = [[node(x=i, y=j) for i in range(4)] for j in range(4)]

        self.scoretext = tk.Label(text=f"Score : {self.score}", font=("ariel", 10, "bold"))
        self.scoretext.place(x=10, y=5)

        self.nodescopy = None
        self.moves = []

        self.__drawborder()
        self.__initmenu()


        for i in range(INITIAL_NODES):
            self.choose_random_node()

        window.bind("<Key>", self.__event_to_move)

        self.window.update()


    def __initmenu(self):
        mainMenu = tk.Menu(self.window)

        optionsMenu = tk.Menu(mainMenu, tearoff=False)
        mainMenu.add_cascade(label="Options", menu=optionsMenu)

        optionsMenu.add_command(label="Restart", command=self.hard_reset)
        optionsMenu.add_separator()
        optionsMenu.add_command(label="Exit", command=self.window.destroy)

        self.window.config(menu=mainMenu)

    def __event_to_move(self, event):
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

    def __drawborder(self):
        for i in range(1, 4):
            self.canvasmain.create_line(101 * i, 0, 101 * i, 404)  # VERT
            self.canvasmain.create_line(0, (101 * i), 404, (101 * i))  # HOR
        self.canvasmain.create_line(0, 1, 404, 1)

    def __clear_flags(self):
        for row in self.nodes:
            for enode in row:
                enode.changed_curr_pass = False

    def choose_random_node(self):
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

    def make_move(self, direction: str):
        if not valid_move_checker(direction, self.nodes):
            if not self.__check_any_valid_move():
                self.scoretext.config(text=f"GAME OVER!  FINAL SCORE : {self.score}")

                result = tkmessagebox.askretrycancel(master=self.window, title="GAME OVER!",
                                                     message=f"FINAL SCORE : {self.score}", icon=tkmessagebox.INFO)

                if result:
                    self.hard_reset()

                return False
            return False

        self.move_animating = True

        self.__clear_flags()
        self.nodescopy = []
        for row in self.nodes:
            newrow = []
            for enode in row:
                newrow.append(node(x=enode.posx, y=enode.posy, value=enode.value, draw=False))
            self.nodescopy.append(newrow)

        if direction in ("l", "r"):
            self.move_horizontal(direction, self.nodescopy)
        elif direction in ("d", "u"):
            self.move_vertical(direction, self.nodescopy)

        # moves are in format - [{'initial': (2, 3), 'final': (3, 3)},...]

        dist: int = 0
        moved_on_pass = True

        while dist <= 304 and moved_on_pass:
            for move in self.moves:
                ini_pos = move["initial"]
                fin_pos = move["final"]
                diff = [(b - a) * 101 for a, b in zip(ini_pos, fin_pos)]
                if sum(diff) == 0:
                    continue
                if abs(sum(diff)) + 1 > dist:
                    initial = self.nodes[ini_pos[0]][ini_pos[1]]
                    tk.Misc.lift(initial.canvas)
                    sign = -1 if sum(diff) > 0 else 1

                    dx = dist if diff[1] else 0
                    dy = dist if diff[0] else 0
                    nx = ini_pos[1] * 101 - (dx * sign) + 1
                    ny = ini_pos[0] * 101 - (dy * sign) + OFFSET + 1

                    if not ((304 >= nx >= 1) and (304 + OFFSET >= ny >= OFFSET)):
                        break

                    tk.Misc.lift(initial.canvas)
                    initial.canvas.place(x=nx, y=ny)
                    self.window.update()
                    moved_on_pass = True
                else:
                    moved_on_pass = False
            dist += STEP_SIZE
        for move in self.moves:
            self.move_actual(move)

        self.moves = []
        self.nodescopy = []

        if RENDER_NEW_NODE: self.choose_random_node()

        self.move_animating = False

    def move_vertical(self, direction, nodescopy):
        ranges = {"d": [(2, -1, -1), (0, 4), 1], "u": [(1, 4), (0, 4), -1]}

        range1 = ranges[direction][0]
        range2 = ranges[direction][1]
        sign = ranges[direction][2]

        for j in range(*range1):
            for i in range(*range2):
                k = 1
                current = nodescopy[j][i]

                if current.value == 0:
                    continue

                shifted = nodescopy[j + (k * sign)][i]
                while shifted.value == 0:
                    k += 1
                    if 0 <= (j + (k * sign)) <= 3:
                        shifted = nodescopy[j + (k * sign)][i]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = nodescopy[j + (k * sign)][i]
                    if not finalpos.changed_curr_pass:

                        finalpos = nodescopy[j + (k * sign)][i]
                        finalpos.changed_curr_pass = True
                        self.moves.append({"initial": (j, i), "final": (j + (k * sign), i)})
                        finalpos.value, current.value = finalpos.value * 2, 0
                    else:
                        finalpos = nodescopy[j + (k * sign) - (1 * sign)][i]
                        self.moves.append({"initial": (j, i), "final": (j + (k * sign) - (1 * sign), i)})
                        finalpos.value, current.value = current.value, finalpos.value

                else:
                    finalpos = nodescopy[j + (k * sign) - (1 * sign)][i]
                    self.moves.append({"initial": (j, i), "final": (j + (k * sign) - (1 * sign), i)})
                    finalpos.value, current.value = current.value, finalpos.value

    def move_horizontal(self, direction, nodescopy):
        ranges = {"r": [(2, -1, -1), (0, 4), 1], "l": [(1, 4), (0, 4), -1]}

        range1 = ranges[direction][0]
        range2 = ranges[direction][1]
        sign = ranges[direction][2]

        for i in range(*range1):
            for j in range(*range2):
                k = 1
                current = nodescopy[j][i]

                if current.value == 0:
                    continue

                shifted = nodescopy[j][i + (k * sign)]
                while shifted.value == 0:
                    k += 1
                    if 0 <= (i + (k * sign)) <= 3:
                        shifted = nodescopy[j][i + (k * sign)]
                    else:
                        break

                if shifted.value == current.value:
                    finalpos = nodescopy[j][i + (k * sign)]
                    if not finalpos.changed_curr_pass:

                        finalpos = nodescopy[j][i + (k * sign)]
                        finalpos.changed_curr_pass = True
                        self.moves.append({"initial": (j, i), "final": (j, i + (k * sign))})
                        finalpos.value, current.value = finalpos.value * 2, 0
                    else:
                        finalpos = nodescopy[j][i + (k * sign) - (1 * sign)]
                        self.moves.append({"initial": (j, i), "final": (j, i + (k * sign) - (1 * sign))})
                        finalpos.value, current.value = current.value, finalpos.value

                else:
                    finalpos = nodescopy[j][i + (k * sign) - (1 * sign)]
                    self.moves.append({"initial": (j, i), "final": (j, i + (k * sign) - (1 * sign))})
                    finalpos.value, current.value = current.value, finalpos.value

    def move_actual(self, move):
        ini_pos = move["initial"]
        fin_pos = move["final"]

        if ini_pos == fin_pos:
            return

        initial = self.nodes[ini_pos[0]][ini_pos[1]]
        final = self.nodes[fin_pos[0]][fin_pos[1]]

        initial.canvas.place(x=ini_pos[1] * 101 + 1, y=ini_pos[0] * 101 + OFFSET + 1)

        if initial.value == final.value:
            final.increment_val()
            self.score += final.value
            self.scoretext["text"] = f"Score : {self.score}"
        else:
            while final.value < initial.value:
                final.increment_val()

        initial.set_to_empty()
        tk.Misc.lift(final.canvas)
        tk.Misc.lift(initial.canvas)
        self.window.update()

    def __check_any_valid_move(self):
        u, d = valid_move_checker("u", self.nodes), valid_move_checker("d", self.nodes)
        l, r = valid_move_checker("l", self.nodes), valid_move_checker("r", self.nodes)
        return u or d or l or r

    def hard_reset(self):
        self.score = 0
        self.scoretext["text"] = f"Score : {self.score}"

        for row in self.nodes:
            for enode in row:
                enode.set_to_empty()

        for i in range(INITIAL_NODES):
            self.choose_random_node()
