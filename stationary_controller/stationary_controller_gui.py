import os
import socket
import sys
import threading
import tkinter as tk
import turtle
from os.path import isfile, join
from time import sleep
from tkinter import ttk

import numpy as np
from onboard_controller.agv_command import AgvCommand
from tools.agv_socket import AgvSocket

from stationary_controller.mode import Mode
from stationary_controller.styles import AgvStyles
from stationary_controller.waypoint import Waypoint

# Global Constants
SERVER_IP = socket.gethostbyname(socket.gethostname() + ".local")
SERVER_IP = "192.168.0.160"
SERVER_PORT = 1234


class GUI(ttk.Frame):
    """AGV Control GUI"""

    def __init__(self) -> None:
        """Initializer"""
        ttk.Frame.__init__(self)

        # Set title of the non-resizable window
        self.master.title("AGV Controller")
        self.master.resizable(0, 0)
        self.grid()

        # Create an instance of style object and configure it
        self.style = ttk.Style()
        self.style = AgvStyles.config_styles(self.style)

        # Current mode
        self.mode = Mode.Unselected
        self.connected_to_server = False

        # TODO: delete temporarily set the mode automatically to teach.
        # self.mode = Mode.Teach
        # self.mode = Mode.Production

        # Create Paness
        self.create_panes()

        # Populate and place Panes
        self.update_and_grid_panes()

        # Populate panes
        self.populate_map_pane()
        self.populate_waypoints_pane()

        # Initialize waypoint and station tracking variables
        self.waypoints: list[Waypoint] = []
        self.stations: dict[int, tuple[str, Waypoint]] = {}

        # Thread for Map overlay of current position and orientation data
        th = threading.Thread(target=self.show_metrics_on_canvas, daemon=True)
        th.start()

    def show_metrics_on_canvas(self) -> None:
        """Creates the metrics textbox. Updates every 250 milliseconds."""
        sleep(0.5)

        # Create text box for displaying data
        tag = "metrics"
        text_x_cor = -self.canvas.winfo_width() * 0.35
        text_y_cor = -self.canvas.winfo_height() * 0.35
        self.canvas.create_text(text_x_cor, text_y_cor, tags=tag)

        while True:
            # Get data
            x_cor = self.turtle.xcor()
            Y_cor = self.turtle.ycor()
            angle = self.turtle.heading()

            # Compose the content of the textbox
            text = f"X:\t{x_cor:.3f}\nY:\t{Y_cor:.3f}\nAngle:\t{angle:.1f}"

            # Set the textbox content
            self.canvas.itemconfigure(tag, text=text)

            sleep(0.25)

    def create_panes(self) -> None:
        """Creates the different panes and store them as instance variables"""

        self.mode_selection_pane = ttk.Frame(self, style="command.TFrame")
        self.prod_pane = ttk.Frame(self, style="button.TFrame")
        self.teach_pane = ttk.Frame(self, style="display.TFrame")
        self.map_pane = ttk.Frame(self, style="canvas.TFrame")
        self.waypoints_pane = ttk.Frame(self, style="waypoint.TFrame")

    def update_and_grid_panes(self) -> None:
        """Grids the appropriate pane."""

        if self.mode is Mode.Unselected:
            self.populate_mode_selection_pane()
            self.mode_selection_pane.grid(
                row=0,
                column=0,
                sticky=tk.NSEW,
                padx=AgvStyles.PADDING * 2,
                pady=AgvStyles.PADDING * 2,
            )

        if self.mode is Mode.Teach:
            self.populate_teach_pane()
            self.teach_pane.grid(
                row=1,
                column=0,
                sticky=tk.NSEW,
                padx=AgvStyles.PADDING,
                pady=AgvStyles.PADDING,
            )

            self.prod_pane.grid_remove()
            for widget in self.prod_pane.winfo_children():
                widget.destroy()

            self.map_pane.grid(
                row=1,
                column=1,
                rowspan=2,
                sticky=tk.NSEW,
                padx=AgvStyles.PADDING,
                pady=AgvStyles.PADDING,
            )
            self.waypoints_pane.grid(
                row=2,
                column=0,
                # columnspan=2,
                sticky=tk.NSEW,
                padx=AgvStyles.PADDING,
                pady=AgvStyles.PADDING,
            )
            return

        if self.mode is Mode.Production:
            self.populate_prod_pane()
            self.prod_pane.grid(
                row=1,
                column=0,
                sticky=tk.NSEW,
                padx=AgvStyles.PADDING,
                pady=AgvStyles.PADDING,
            )
            self.teach_pane.grid_remove()
            for widget in self.teach_pane.winfo_children():
                widget.destroy()

            self.map_pane.grid(
                row=1,
                column=2,
                rowspan=2,
                sticky=tk.NSEW,
                padx=AgvStyles.PADDING,
                pady=AgvStyles.PADDING,
            )
            self.waypoints_pane.grid_remove()
            return

    def populate_mode_selection_pane(self) -> None:
        """Generate the contents of the mode selection pane."""

        # Create and place the label on the screen
        ttk.Label(self.mode_selection_pane, text="Select AGV Mode:").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=tk.W,
        )

        # Create the buttons
        self.btn_teach_mode = ttk.Button(
            self.mode_selection_pane,
            text="Teach Mode",
            command=self.select_teach_mode,
            style="teach.TButton",
        )
        self.btn_prod_mode = ttk.Button(
            self.mode_selection_pane,
            text="Auto Mode",
            command=self.select_prod_mode,
            style="prod.TButton",
        )

        # place the buttons on the screen
        self.btn_teach_mode.grid(
            row=1, column=0, sticky=tk.EW, padx=AgvStyles.PADDING
        )
        self.btn_prod_mode.grid(
            row=1, column=1, sticky=tk.EW, padx=AgvStyles.PADDING
        )

        if self.connected_to_server:
            return

        self.btn_connect_to_server = ttk.Button(
            self.mode_selection_pane,
            text="Connect to Server",
            style="serverconn.TButton",
            command=self.connect_to_server,
        )
        self.btn_connect_to_server.grid(
            row=1, column=2, sticky=tk.EW, padx=AgvStyles.PADDING
        )

    def connect_to_server(self):
        self.client = AgvSocket(
            ip=SERVER_IP, port=SERVER_PORT, isServer=False
        )
        self.btn_connect_to_server.state(["disabled"])
        self.style.map(
            "serverconn.TButton", background=[("disabled", "white")]
        )
        self.btn_connect_to_server.config(text="Connected")

    def select_teach_mode(self) -> None:
        """Handles selecting the teach mode button."""

        # Set the mode to teach
        self.mode = Mode.Teach

        # Disable and enable the appropriate buttons
        self.btn_prod_mode.state(["!disabled"])
        self.btn_teach_mode.state(["disabled"])

        # Change the background of the selected button
        self.style.map("prod.TButton", background=[("alternate", "#fcc200")])
        self.style.map("teach.TButton", background=[("disabled", "green")])

        # Send to server
        self.client.send_message(msg=f"{AgvCommand.set_mode.value} TEACH")

        # Grid the appropriate pane
        self.update_and_grid_panes()

    def select_prod_mode(self) -> None:
        """Handles selecting the production mode button"""

        # Set the mode to production
        self.mode = Mode.Production

        # Disable and enable the appropriate buttons
        self.btn_teach_mode.state(["!disabled"])
        self.btn_prod_mode.state(["disabled"])

        # Change the background of the selected button
        self.style.map("teach.TButton", background=[("alternate", "#fcc200")])
        self.style.map("prod.TButton", background=[("disabled", "green")])

        # Send to server
        self.client.send_message(msg=f"{AgvCommand.set_mode.value} AUTO")

        # Grid the appropriate pane
        self.update_and_grid_panes()

    def populate_prod_pane(self) -> None:
        """Generate the contents of the production pane."""

        # Create and place labels on the screen
        ttk.Label(self.prod_pane, text="Starting Station:").grid(
            row=1,
            column=0,
            sticky=tk.W,
        )
        ttk.Label(self.prod_pane, text="Destination:").grid(
            row=2,
            column=0,
            sticky=tk.W,
        )

        # options to appear in the dropdown menu
        self.dd_destinations_options = self.set_dd_destination_var()

        # Selected option from the starting dropdown menu
        self.dd_var_starting_station = tk.StringVar()

        # Starting dropdown menu
        self.dd_starting_station = ttk.OptionMenu(
            self.prod_pane,
            self.dd_var_starting_station,
            self.dd_destinations_options[0],
            *self.dd_destinations_options,
        )

        # Selected option from the destination dropdown menu
        self.dd_var_destination_station = tk.StringVar()

        # Destination dropdown menu
        self.dd_destination_station = ttk.OptionMenu(
            self.prod_pane,
            self.dd_var_destination_station,
            self.dd_destinations_options[0],
            *self.dd_destinations_options,
        )

        # Place dropdown menus on the screen
        self.dd_starting_station.grid(row=1, column=1)
        self.dd_destination_station.grid(row=2, column=1)

        # Create and place the load button on the screen
        ttk.Button(
            self.prod_pane,
            text="Load Route",
            command=self.load_route,
        ).grid()

    def get_route_files(self) -> list[str]:
        """Returns a list of all file names in the routes directory

        Returns:
            list[str]: list of file names
        """

        # Relative location of the routes directory
        routes_path = "./routes/"

        # Get the file names
        onlyfiles = [
            f for f in os.listdir(routes_path) if isfile(join(routes_path, f))
        ]
        return onlyfiles

    def set_dd_destination_var(self) -> list[str]:
        """Generates the list of stations based on the saved routes.

        Returns:
            list[str]: list of destination options
        """

        files = self.get_route_files()

        # Remove the .txt file extension for each list item
        stations = [f[:-4].split("_to_") for f in files]

        # Remove duplicate station values
        stations = np.unique(stations)

        # Sort the station values alphabetically
        stations.sort()
        return list(stations)

    def load_route(self) -> None:
        """Loads the selected route from the routes directory."""

        waypoints: list[Waypoint] = []
        starting_name = self.dd_var_starting_station.get()
        destination_name = self.dd_var_destination_station.get()
        file_name = f"{starting_name}_to_{destination_name}.txt"

        files: list[str] = self.get_route_files()
        if file_name not in files:
            print("Selected route not found in the saved routes.")
            return

        # Remove the previously loaded stations
        for _ in range(len(self.stations)):
            self.remove_station()

        # Open the file to in read mode
        with open(file=f"./routes/{file_name}", mode="r") as file:
            # Ignore the heading (first line)
            file.readline()

            # Store instructions in a list
            instructions: list[str] = file.readlines()

            for i, inst in enumerate(instructions):
                # Remove the trailing "\n".
                inst: str = inst.strip()

                # Transform the string to a list of string coordinates.
                wp_list: list[str] = inst.split(" ")

                x_cor = float(wp_list[0])
                y_cor = float(wp_list[1])
                angle = float(wp_list[2])

                wp = Waypoint(x=x_cor, y=y_cor, heading=angle)

                waypoints.append(wp)

                # If the first instruction (starting station)
                if i == 0:
                    n = len(self.stations)
                    self.stations[n] = (starting_name, wp)

                    self.draw_station(station=wp, name=starting_name)

                # If the last instruction (destination station)
                if i == len(instructions) - 1:
                    n = len(self.stations)
                    self.stations[n] = (destination_name, wp)

                    self.draw_station(station=wp, name=destination_name)

        self.traverse_waypoints(waypoints=waypoints, set_waypoints=True)
        print(
            f'Route "{starting_name}" to "{destination_name}" \
                 loaded from file {file_name} successfully.'
        )

    def traverse_waypoints(
        self, waypoints: list[Waypoint], set_waypoints: bool = False
    ) -> None:
        """_summary_

        Args:
            waypoints (list[Waypoint]): _description_
            set_waypoints (bool, optional): _description_. Defaults to False.
        """
        self.initialize_turtle()
        self.turtle.pencolor("black")
        if set_waypoints:
            self.waypoints = []

        for wp in waypoints:
            self.turtle.goto(x=wp.x, y=wp.y)
            self.turtle.setheading(wp.heading)
            if set_waypoints:
                self.waypoints.append(wp)

    def initialize_turtle(self):
        self.turtle.reset()
        self.turtle.clear()
        self.turtle.left(90)

    def move_forward(self, dist: int = 10) -> None:
        dist = self.txt_intensity_value.get()
        self.turtle.forward(dist)

        text = f"{AgvCommand.forward.value} {dist}"
        self.client.send_message(text)

    def move_backward(self, dist: int = 10):
        dist = self.txt_intensity_value.get()
        self.turtle.backward(dist)

        text = f"{AgvCommand.backward.value} {dist}"
        self.client.send_message(text)

    def rotate_left(self, angle: int = 10):
        angle = self.txt_intensity_value.get()
        self.turtle.left(angle)

        text = f"{AgvCommand.rotate_ccw.value} {angle}"
        self.client.send_message(text)

    def rotate_right(self, angle: int = 10):
        angle = self.txt_intensity_value.get()
        self.turtle.right(angle)

        text = f"{AgvCommand.rotate_cw.value} {angle}"
        self.client.send_message(text)

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

    def save_route(self):
        if len(self.stations) != 2:
            print(
                f"Two stations must exist but only {len(self.stations)} \
                    was found."
            )
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

    def add_station(self):
        if not self.waypoints:
            print(
                "No waypoints exist. First add a waypoint \
                    before adding a station."
            )
            return

        if not self.txt_var_station_name.get():
            print("No station name entered. First add a station name.")
            return

        station = self.waypoints[-1]
        name = self.txt_var_station_name.get().strip()
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
        print(
            f'Removed station "{self.stations[index][0]}" at {self.stations[index][1]}'
        )
        self.canvas.delete(tag)
        self.stations.pop(index)

        if self.mode == Mode.Production:
            return

        if len(self.stations) == 0:
            self.btn_add_station.configure(text="+ Starting Station")
        elif len(self.stations) == 1:
            self.btn_add_station.configure(
                text="+ Destination", state="normal"
            )

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
            command=self.halt,
        )
        self.btn_emergency_stop = ttk.Button(
            self.teach_pane,
            text="E-Stop",
            style="estop.TButton",
            command=self.emergency_stop,
        )
        self.btn_calibrate_home = ttk.Button(
            self.teach_pane,
            text="Calibrate Home",
            command=lambda: (
                self.traverse_waypoints(self.waypoints),
                self.client.send_message(
                    f"{AgvCommand.calibrate_home.value} {0}"
                ),
            ),
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

        self.txt_var_station_name = tk.StringVar()
        self.txt_var_station_name.set("Station Name")
        self.txt_station_name = ttk.Entry(
            self.teach_pane,
            textvariable=self.txt_var_station_name,
            font=(None, AgvStyles.FONT_SIZE),
        )
        self.txt_station_name.bind(
            "<Button-1>", lambda event: self.on_click_txt_station_name(event)
        )

        self.txt_intensity_value = tk.IntVar(value=10)
        self.txt_intensity = ttk.Entry(
            self.teach_pane,
            textvariable=self.txt_intensity_value,
            font=(None, AgvStyles.FONT_SIZE),
        )

        # Place Elements
        # Row 1
        self.btn_add_waypoint.grid(row=1, column=0)
        self.btn_move_forward.grid(row=1, column=1)
        self.btn_remove_waypoint.grid(row=1, column=2)

        # Row 2
        self.btn_rotate_left.grid(row=2, column=0, sticky=tk.E)
        self.btn_calibrate_home.grid(
            row=2, column=1, pady=AgvStyles.PADDING, padx=AgvStyles.PADDING
        )
        self.btn_rotate_right.grid(row=2, column=2, sticky=tk.W)

        # Row 3
        self.btn_halt.grid(row=3, column=0)
        self.btn_move_backward.grid(row=3, column=1)
        self.btn_emergency_stop.grid(row=3, column=2)

        # Row 4
        ttk.Label(
            self.teach_pane, text="Set intensity [1, 10] (inches):"
        ).grid(row=4, column=0, sticky=tk.E)
        self.txt_intensity.grid(
            row=4, column=1, pady=AgvStyles.PADDING, sticky=tk.W
        )

        # Row 5
        self.btn_add_station.grid(
            row=5, column=0, padx=AgvStyles.PADDING, pady=AgvStyles.PADDING
        )
        self.txt_station_name.grid(row=5, column=1)
        btn_remove_station.grid(row=5, column=2, padx=AgvStyles.PADDING)

        # Row 6
        btn_save_route.grid(row=6, column=1)

    def halt(self):
        self.client.send_message(AgvCommand.halt.value)

    def emergency_stop(self):
        self.client.send_message(AgvCommand.e_stop.value)

    def on_click_txt_station_name(self, event):
        self.txt_var_station_name.set("")

    def populate_map_pane(self):
        ttk.Label(self.map_pane, text="Map").grid(sticky=tk.N)
        self.canvas = turtle.ScrolledCanvas(self.map_pane)
        self.canvas.grid(row=1, column=0)
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.screensize(1000, 1000)
        self.turtle = turtle.RawTurtle(self.canvas)
        self.initialize_turtle()

    def populate_waypoints_pane(self):
        self.lbl_str_var = tk.StringVar(value="Current Waypoints:\n")
        self.lbl_waypoints = ttk.Label(
            self.waypoints_pane,
            textvariable=self.lbl_str_var,
            font=("Arial", AgvStyles.FONT_SIZE - 5),
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
        self.lbl_str_var.set(result)


def main():
    """Run AGV Control GUI"""
    GUI().mainloop()


if __name__ == "__main__":
    main()
