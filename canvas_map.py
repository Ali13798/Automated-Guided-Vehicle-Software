import tkinter as tk
import turtle
from tkinter import ttk


class CanvasMap:
    def __init__(self, window: tk.Frame) -> None:
        self.canvas = turtle.ScrolledCanvas(window)
        self.screen = turtle.TurtleScreen(self.canvas)
        self.turtle = turtle.RawTurtle(self.canvas)
        self.turtle.left(90)
        self.get_ccords()

    def get_ccords(self):
        self.cur_x = self.turtle.xcor()
        self.cur_y = self.turtle.ycor()
        self.cur_ang = self.turtle.heading()
        print(f"x: {self.cur_x}\ny: {self.cur_y}\nangle: {self.cur_ang}")

    def grid(self, row: int, col: int) -> None:
        self.canvas.grid(row=row, column=col, sticky=tk.NSEW)

    def move_up(self):
        self.turtle.forward(100)

    def focus(self):
        self.canvas.focus_set()
