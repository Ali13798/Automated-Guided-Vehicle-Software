import tkinter as tk
import turtle
from tkinter import ttk

from mode import Mode
from styles import AgvStyles

FONT_SIZE = 20
PADDING = 10


class GUI(ttk.Frame):
    """AGV Control GUI"""

    def __init__(self) -> None:
        # Initialize
        ttk.Frame.__init__(self)

        # Set title
        self.master.title("AGV Controller")
        self.master.resizable(0, 0)
        self.grid()

        # Create an instance of style object and configure it
        self.style = ttk.Style()
        self.style = AgvStyles.config_styles(self.style)

        # Current mode
        self.mode = Mode.Unselected

        # Create Paness
        self.create_panes()

        # Grid Panes
        self.grid_panes()

        # Populate panes
        self.populate_top_pane()
        self.populate_prod_pane()
        self.populate_teach_pane()
        self.populate_map_pane()

    def create_panes(self) -> None:
        self.mode_selection_pane = ttk.Frame(self, style="command.TFrame", padding=10)
        self.prod_pane = ttk.Frame(self, style="button.TFrame", padding=10)
        self.teach_pane = ttk.Frame(self, style="display.TFrame", padding=10)
        self.map_pane = ttk.Frame(self, style="canvas.TFrame", padding=10)

    def grid_panes(self):
        if self.mode is Mode.Unselected:
            self.mode_selection_pane.grid(row=0, column=0, sticky=tk.NSEW)
        elif self.mode is Mode.Teach:
            self.teach_pane.grid(row=1, column=0, sticky=tk.NSEW)
            self.prod_pane.grid_remove()
            self.map_pane.grid(row=1, column=2)
        elif self.mode is Mode.Production:
            self.prod_pane.grid(row=1, column=0, sticky=tk.NSEW)
            self.teach_pane.grid_remove()
            self.map_pane.grid(row=1, column=2)

    def populate_top_pane(self):
        ttk.Label(self.mode_selection_pane, text="Select AGV Mode:").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=tk.W,
        )
        self.btn_teach_mode = ttk.Button(
            self.mode_selection_pane,
            text="Teach Mode",
            command=self.select_teach_mode,
            style="teach.TButton",
        )
        self.btn_teach_mode.grid(row=1, column=0, sticky=tk.EW, padx=PADDING)

        self.btn_prod_mode = ttk.Button(
            self.mode_selection_pane,
            text="Auto Mode",
            command=self.select_prod_mode,
            style="prod.TButton",
        )
        self.btn_prod_mode.grid(row=1, column=1, sticky=tk.EW, padx=PADDING)

    def select_teach_mode(self):
        self.mode = Mode.Teach
        self.btn_prod_mode.state(["!disabled"])
        self.btn_teach_mode.state(["disabled"])
        self.style.map("prod.TButton", background=[("alternate", "#fcc200")])
        self.style.map("teach.TButton", background=[("disabled", "green")])
        self.grid_panes()

    def select_prod_mode(self):
        self.mode = Mode.Production
        self.btn_teach_mode.state(["!disabled"])
        self.btn_prod_mode.state(["disabled"])
        self.style.map("teach.TButton", background=[("alternate", "#fcc200")])
        self.style.map("prod.TButton", background=[("disabled", "green")])
        self.grid_panes()

    def populate_prod_pane(self):
        ttk.Label(self.prod_pane, text="Starting Station:").grid(
            row=1,
            column=0,
            sticky=tk.W,
        )

        self.dd_var_destinations = tk.StringVar()
        self.txt_starting_point = ttk.Entry(
            self.prod_pane,
            textvariable=self.dd_var_destinations,
            font=(None, FONT_SIZE),
        )
        self.txt_starting_point.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(self.prod_pane, text="Destination:").grid(
            row=2,
            column=0,
            sticky=tk.W,
        )

        self.txt_var_destination_point = tk.StringVar()
        self.txt_destination_point = ttk.Entry(
            self.prod_pane,
            textvariable=self.txt_var_destination_point,
            font=(None, FONT_SIZE),
        )
        self.txt_destination_point.grid(row=2, column=1, sticky=tk.W)

    def populate_teach_pane(self) -> None:
        # Create Control Buttons
        ttk.Label(self.teach_pane, text="Controls").grid(row=0, column=1)
        self.btn_move_forward = ttk.Button(
            self.teach_pane,
            text="↑",
            style="control.TButton",
        )
        self.btn_move_backward = ttk.Button(
            self.teach_pane,
            text="↓",
            style="control.TButton",
        )
        self.btn_rotate_left = ttk.Button(
            self.teach_pane,
            text="←",
            style="control.TButton",
        )
        self.btn_rotate_right = ttk.Button(
            self.teach_pane,
            text="→",
            style="control.TButton",
        )
        self.btn_halt = ttk.Button(
            self.teach_pane,
            text="Halt",
        )
        self.btn_emergency_stop = ttk.Button(
            self.teach_pane,
            text="E-Stop",
        )
        self.btn_calibrate_home = ttk.Button(
            self.teach_pane,
            text="Calibrate Home",
        )
        self.btn_add_waypoint = ttk.Button(
            self.teach_pane,
            text="+ Waypoint",
        )
        self.btn_remove_waypoint = ttk.Button(
            self.teach_pane,
            text="- Waypoint",
        )

        self.dd_destinations_options = ["A", "B", "C", "D"]
        self.dd_var_destinations = tk.StringVar()
        self.dd_destinations = ttk.OptionMenu(
            self.teach_pane,
            self.dd_var_destinations,
            self.dd_destinations_options[0],
            *self.dd_destinations_options,
        )

        # Grid Control Buttons
        self.btn_add_waypoint.grid(row=1, column=0)
        self.btn_move_forward.grid(row=1, column=1)
        self.btn_remove_waypoint.grid(row=1, column=2)
        self.btn_rotate_right.grid(row=2, column=2, sticky=tk.W)
        self.btn_rotate_left.grid(row=2, column=0, sticky=tk.E)
        self.btn_move_backward.grid(row=3, column=1)
        self.btn_halt.grid(row=3, column=0)
        self.btn_emergency_stop.grid(row=3, column=2)
        self.btn_calibrate_home.grid(row=2, column=1, pady=PADDING, padx=PADDING)
        self.dd_destinations.grid()

    def populate_map_pane(self):
        ttk.Label(self.map_pane, text="Map").grid(sticky=tk.N)
        self.canvas = turtle.ScrolledCanvas(self.map_pane)
        self.canvas.grid()
        self.screen = turtle.TurtleScreen(self.canvas)
        self.turtle = turtle.RawTurtle(self.canvas)


def main():
    """Run AGV Control GUI"""
    GUI().mainloop()


if __name__ == "__main__":
    main()
