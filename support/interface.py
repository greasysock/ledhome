# https://pihw.wordpress.com/lessons/rgb-led-lessons/rgb-led-lesson-5-creating-a-graphical-user-interface/ Inspired from this tutorial
import time, sys, os, resource, threading, enum
from tkinter import *

# Set display sizes
WINDOW_W = 500
WINDOW_H = 100

# Set display sizes
BUTTON_SIZE = 25
NUM_BUTTON = 5
MARGIN = 5
WINDOW_W = MARGIN + ((BUTTON_SIZE + MARGIN) * NUM_BUTTON)
WINDOW_H = (2 * MARGIN) + BUTTON_SIZE

# Set colours
# R G B
BLACK = '#000000'
BRIGHTRED = '#ff0000'
RED = '#9b0000'

class Led():
    def __init__(self, rectangle_object):
        pass

class LedPanel(Tk):
    def __init__(self, leds):
        Tk.__init__(self)
        self._window_width = leds * (BUTTON_SIZE + MARGIN)
        self._canvas = Canvas(self, width=self._window_width, height=WINDOW_H, background=BLACK)
        self._canvas.pack()
        self._leds = []
        self._leds_num = leds
        for i in range(leds):
            x = MARGIN + ((MARGIN + BUTTON_SIZE) * i)
            rect = self._canvas.create_rectangle(x, MARGIN,x + BUTTON_SIZE, BUTTON_SIZE + MARGIN, fill=RED)
            self._leds.append(rect)
        btn = Button(self, text="Exit", command=self.terminate)
        btn.pack()
    def write(self, led_data):
        for led in range(self._leds_num):
            start_index = 4 * led
            data = led_data[start_index:start_index+4]
            color_code = '#%02x%02x%02x' % (data[3], data[2], data[1])
            l = led + 1
            self._canvas.itemconfig(l, fill=color_code)
    def start(self):
        self.mainloop()
    def terminate(self):
        self.destroy()

