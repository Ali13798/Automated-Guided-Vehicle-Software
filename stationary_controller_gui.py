import tkinter as tk
import turtle
from tkinter import ttk

from mode import Mode
from styles import AgvStyles
from waypoint import Waypoint

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

        # TODO: delete temporarily set the mode automatically to teach.
        self.mode = Mode.Teach

        # Create Paness
        self.create_panes()

        # Grid Panes
        self.grid_panes()

        # Populate panes
        self.populate_top_pane()
        self.populate_map_pane()
        self.populate_prod_pane()
        self.populate_teach_pane()
        self.populate_waypoints_pane()

        self.waypoints: list[Waypoint] = []
        self.stations: dict[int, tuple[str, Waypoint]] = {}

    def create_panes(self) -> None:
        self.mode_selection_pane = ttk.Frame(self, style="command.TFrame", padding=10)
        self.prod_pane = ttk.Frame(self, style="button.TFrame", padding=PADDING)
        self.teach_pane = ttk.Frame(self, style="display.TFrame", padding=PADDING)
        self.map_pane = ttk.Frame(self, style="canvas.TFrame", padding=PADDING)
        self.waypoints_pane = ttk.Frame(self, style="waypoint.TFrame", padding=PADDING)

    def grid_panes(self):
        if self.mode is Mode.Unselected:
            self.mode_selection_pane.grid(row=0, column=0, sticky=tk.NSEW)
        elif self.mode is Mode.Teach:
            self.teach_pane.grid(row=1, column=0, sticky=tk.NSEW)
            self.prod_pane.grid_remove()
            self.map_pane.grid(row=1, column=1, sticky=tk.NSEW)
            self.waypoints_pane.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)
        elif self.mode is Mode.Production:
            self.prod_pane.grid(row=1, column=0, sticky=tk.NSEW)
            self.teach_pane.grid_remove()
            self.map_pane.grid(row=1, column=2)
            self.waypoints_pane.grid_remove()

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

        self.txt_var_starting_point = tk.StringVar()
        self.txt_starting_point = ttk.Entry(
            self.prod_pane,
            textvariable=self.txt_var_starting_point,
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

    def move_forward(self, dist: int = 10) -> None:
        self.turtle.forward(dist)

    def move_backward(self, dist: int = 10):
        self.turtle.backward(dist)

    def rotate_left(self, angle: int = 10):
        self.turtle.left(angle)

    def rotate_right(self, angle: int = 10):
        self.turtle.right(angle)

    def store_waypoint(self):
        x = self.turtle.xcor()
        y = self.turtle.ycor()
        heading = self.turtle.heading()
        wp = Waypoint(x=x, y=y, heading=heading)
        if not self.waypoints or wp != self.waypoints[-1]:
            self.waypoints.append(wp)
            self.update_waypoint_label()
            print(f"Stored waypoint: {wp}")
        else:
            print("Not a new waypoint. Jog the AGV then try again.")

    def remove_waypoint(self):
        print()
        if not self.waypoints:
            print("No more waypoints stored.")
            return

        cur_waypoint = self.waypoints.pop()
        self.traverse_waypoints(self.waypoints)
        self.update_waypoint_label()
        print(f"Removed {cur_waypoint}")
        print(f"Remaining waypoints:\n{self.waypoints}")

    def traverse_waypoints(self, waypoints: list[Waypoint]):
        self.initialize_turtle()
        self.turtle.pencolor("black")
        for wp in waypoints:
            self.turtle.goto(x=wp.x, y=wp.y)
            self.turtle.setheading(wp.heading)

    def initialize_turtle(self):
        self.turtle.reset()
        self.turtle.clear()
        self.turtle.left(90)

    def save_route(self, file_name="A_to_B.txt"):
        if len(self.stations) != 2:
            print(f"Two stations must exist but only {len(self.stations)} was found.")
            return

        file_name = f"{self.stations[0][0]}_to_{self.stations[1][0]}.txt"

        with open(file=f"./routes/{file_name}", mode="w") as file:
            file.write("X Y HEADING\n")
            for wp in self.waypoints:
                x = 0 if (wp.x < 0.001 and wp.x > -0.001) else wp.x
                y = 0 if (wp.y < 0.001 and wp.y > -0.001) else wp.y
                inst = f"{x} {y} {wp.heading}\n"
                file.writelines(inst)

        print(f"Route {file_name[:-4]} successfully saved.")

    def load_route(self, file_name="A_to_B.txt"):
        self.lwp = []

        with open(file=f"./routes/{file_name}", mode="r") as file:
            # Ignore the heading (first line)
            file.readline()

            # Store instructions in a list
            instructions = file.readlines()
            for inst in instructions:
                # Remove the leading \n.
                inst: str = inst.strip()

                # Transform the string to a list of string coordinates.
                wp: list[str] = inst.split(" ")

                x = float(wp[0])
                y = float(wp[1])
                heading = float(wp[2])

                self.lwp.append(Waypoint(x=x, y=y, heading=heading))

        self.traverse_waypoints(self.lwp)

    def add_station(self):
        if not self.waypoints:
            print("No waypoints exist. First add a waypoint before adding a station.")
            return

        if not self.txt_var_station_name.get():
            print("No station name entered. First add a station name.")
            return

        station = self.waypoints[-1]
        name = self.txt_var_station_name.get()
        index = len(self.stations)
        self.stations[index] = (name, station)
        self.txt_var_station_name.set("")

        if len(self.stations) == 1:
            print(f'Added starting station "{name}" at {station}')
            self.btn_add_station.configure(text="+ Destination")
        elif len(self.stations) == 2:
            print(f'Added destination "{name}" at {station}')
            self.btn_add_station.configure(state="disabled")
        else:
            print("Error: More than two stations found.")

        self.draw_station(station, name)

    def draw_station(self, station: Waypoint, name: str):
        radius = 4
        top_left_x = station.x + radius
        top_left_y = -(station.y + radius)
        bot_right_x = station.x - radius
        bot_right_y = -station.y + radius
        tag = f"station{len(self.stations)}"

        self.canvas.create_oval(
            top_left_x,
            top_left_y,
            bot_right_x,
            bot_right_y,
            outline="red",
            tags=tag,
        )
        self.canvas.create_text(
            station.x, -station.y + 10, text=name, fill="red", tags=tag
        )

    def remove_station(self):
        if not self.stations:
            print("No stations found.")
            return

        tag = f"station{len(self.stations)}"
        index = len(self.stations) - 1
        print(f"Removed station {self.stations[index][0]} at {self.stations[index][1]}")
        self.canvas.delete(tag)
        self.stations.pop(index)
        if len(self.stations) == 0:
            self.btn_add_station.configure(text="+ Starting Station")
        elif len(self.stations) == 1:
            self.btn_add_station.configure(text="+ Destination", state="normal")

    def populate_teach_pane(self) -> None:
        # Create Control Buttons
        ttk.Label(self.teach_pane, text="Controls").grid(row=0, column=1)
        self.btn_move_forward = ttk.Button(
            self.teach_pane,
            text="↑",
            style="control.TButton",
            command=self.move_forward,
        )
        self.btn_move_backward = ttk.Button(
            self.teach_pane,
            text="↓",
            style="control.TButton",
            command=self.move_backward,
        )
        self.btn_rotate_left = ttk.Button(
            self.teach_pane,
            text="←",
            style="control.TButton",
            command=self.rotate_left,
        )
        self.btn_rotate_right = ttk.Button(
            self.teach_pane,
            text="→",
            style="control.TButton",
            command=self.rotate_right,
        )
        self.btn_halt = ttk.Button(
            self.teach_pane,
            text="Halt",
            command=self.load_route,
        )
        self.btn_emergency_stop = ttk.Button(
            self.teach_pane,
            text="E-Stop",
            command=lambda: print(self.waypoints),
        )
        self.btn_calibrate_home = ttk.Button(
            self.teach_pane,
            text="Calibrate Home",
            command=lambda: self.traverse_waypoints(self.waypoints),
        )
        self.btn_add_waypoint = ttk.Button(
            self.teach_pane,
            text="+ Waypoint",
            command=self.store_waypoint,
        )
        self.btn_remove_waypoint = ttk.Button(
            self.teach_pane,
            text="- Waypoint",
            command=self.remove_waypoint,
        )
        self.btn_add_station = ttk.Button(
            self.teach_pane,
            text="+ Starting Station",
            command=self.add_station,
        )
        btn_remove_station = ttk.Button(
            self.teach_pane,
            text="- Station",
            command=self.remove_station,
        )
        btn_save_route = ttk.Button(
            self.teach_pane,
            text="Save Route",
            command=self.save_route,
        )

        self.dd_destinations_options = ["A", "B", "C", "D"]
        self.dd_var_destinations = tk.StringVar()
        self.dd_destinations = ttk.OptionMenu(
            self.teach_pane,
            self.dd_var_destinations,
            self.dd_destinations_options[0],
            *self.dd_destinations_options,
        )

        self.txt_var_station_name = tk.StringVar()
        self.txt_var_station_name.set("Station Name")
        self.txt_station_name = ttk.Entry(
            self.teach_pane,
            textvariable=self.txt_var_station_name,
            font=(None, FONT_SIZE),
        )
        self.txt_station_name.bind("<Button-1>", lambda event: self.on_click(event))

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
        self.dd_destinations.grid(row=4)
        self.btn_add_station.grid(row=5, column=0, padx=PADDING, pady=PADDING)
        self.txt_station_name.grid(row=5, column=1)
        btn_remove_station.grid(row=5, column=2, padx=PADDING)
        btn_save_route.grid()

    def on_click(self, event):
        self.txt_var_station_name.set("")

    def populate_map_pane(self):
        ttk.Label(self.map_pane, text="Map").grid(sticky=tk.N)
        self.canvas = turtle.ScrolledCanvas(self.map_pane)
        self.canvas.grid(row=1, column=0)
        self.screen = turtle.TurtleScreen(self.canvas)
        self.turtle = turtle.RawTurtle(self.canvas)
        self.initialize_turtle()

    def populate_waypoints_pane(self):
        self.lbl_str_var = tk.StringVar(value="Current Waypoints:\n")
        self.lbl_waypoints = ttk.Label(
            self.waypoints_pane,
            textvariable=self.lbl_str_var,
            font=("Arial", FONT_SIZE - 5),
        )
        self.lbl_waypoints.grid()

    def update_waypoint_label(self):
        n_disp = 5
        result = (
            "Current Waypoints:\n"
            if len(self.waypoints) < n_disp + 1
            else "Last 5 Waypoints:\n"
        )
        for i, wp in enumerate(self.waypoints):
            if len(self.waypoints) - n_disp - 1 < i:
                line = f"Waypoint {i+1}: {wp}\n"
                result += line
                # cur_text = self.lbl_str_var.get()
                # new_text = f"{cur_text}Waypoint {len(self.waypoints)}: {wp}\n"
        self.lbl_str_var.set(result)


def main():
    """Run AGV Control GUI"""
    GUI().mainloop()


if __name__ == "__main__":
    main()
