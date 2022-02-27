from tkinter import ttk


class GUI(ttk.Frame):
    """AGV Control GUI"""

    def __init__(self):
        # Initialize
        ttk.Frame.__init__(self, padding=10)
        self.master.title("AGV Controller")
        self.grid()

        # create an instance of style object
        self.style = ttk.Style()

        self.create_panes()

        self.create_control_buttons()

        self.configure_styles()

    def create_panes(self):
        # Create Panes
        self.display_pane = ttk.Frame(self, style="button.TFrame", padding=10)
        self.control_pane = ttk.Frame(self, style="display.TFrame", padding=10)
        self.command_pane = ttk.Frame(self, style="command.TFrame", padding=10)

        # Grid Panes
        self.display_pane.grid(row=0, column=0)
        self.control_pane.grid(row=1, column=0)
        self.command_pane.grid(row=2, column=0)

    def create_control_buttons(self):
        # Create Control Buttons
        self.btn_move_forward = ttk.Button(
            self.control_pane,
            text="↑",
            style="control.TButton",
        )
        self.btn_move_backward = ttk.Button(
            self.control_pane,
            text="↓",
            style="control.TButton",
        )
        self.btn_rotate_left = ttk.Button(
            self.control_pane,
            text="←",
            style="control.TButton",
        )
        self.btn_rotate_right = ttk.Button(
            self.control_pane,
            text="→",
            style="control.TButton",
        )

        # Grid Control Buttons
        self.btn_move_forward.grid(row=0, column=1)
        self.btn_move_backward.grid(row=2, column=1)
        self.btn_rotate_right.grid(row=1, column=2)
        self.btn_rotate_left.grid(row=1, column=0)

    def configure_styles(self):
        # Configure styles
        self.style.configure(
            "control.TButton",
            padding=0,
            background="#1cc",
            width=4,
            font=(None, 25),
        )
        self.style.configure(
            "Tlabel",
        )
        self.style.configure(
            "button.TFrame",
            background="#fcc200",
        )
        self.style.configure(
            "display.TFrame",
            background="maroon",
        )


def main():
    """Run AGV Control GUI"""
    GUI().mainloop()


if __name__ == "__main__":
    main()
