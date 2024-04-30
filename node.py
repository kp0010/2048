import tkinter
import colorsys
from config import *


def calc_color(value):
    hex_color = NODE_COLOR
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


class node:
    def __init__(self, x=0, y=0, value=0, draw=True, changed=False, root=None):
        super().__init__()
        self.pos = (x, y)
        self.posx, self.posy = self.pos
        self.value = value
        self.changed_curr_pass = changed
        if draw:
            self.label = tkinter.Label(root, text="", font=("ARIAL", 15, "bold"), height=2,
                                       borderwidth=0, highlightthickness=0, bg=EMPTY_COLOR, fg="black")
            self._nodetopos(self.posx, self.posy)
            if value != 0:
                self._change_color(self.value)
                self.label["text"] = value


    def increment_val(self, incr=True):
        if incr:
            if self.value == 0:
                self.value = 1
            self.value *= 2
            self._change_val(self.value)
        else:
            self._change_color(self.value)
        return self.value

    def set_to_empty(self):
        self.value = 0
        self._change_val("")
        self.label["bg"] = EMPTY_COLOR

    def _change_val(self, value):
        self._change_color(self.value)
        self.label["text"] = value

    def _nodetopos(self, px, py):
        self.label.place(x=px * 101 + 1, y=(py * 101) + 1, relwidth=0.2475, relheight=0.2475)

    def _change_color(self, value):
        col = calc_color(value)
        self.label.config(bg=col)

    def __repr__(self):
        return f"{self.value = }, {self.pos = }"

    def __str__(self):
        return f"{self.value = }, {self.pos = }"
