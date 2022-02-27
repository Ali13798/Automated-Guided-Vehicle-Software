from tkinter import ttk


class GUI(ttk.Frame):
    """AGV Control GUI"""

    def __init__(self):
        # Initialize
        ttk.Frame.__init__(self, padding=10)
        self.master.title("AGV Controller")
        self.grid()

        # create an instance of style object
        style = ttk.Style()

        # Create Panes
        self.display_pane = ttk.Frame(self, style="button.TFrame", padding=10)
        self.control_pane = ttk.Frame(self, style="display.TFrame", padding=10)

        # Grid Panes
        self.display_pane.grid(row=0, column=0)
        self.control_pane.grid(row=1, column=0)

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

        # Configure styles
        style.configure(
            "control.TButton",
            padding=0,
            background="#1cc",
            width=4,
            font=(None, 25),
        )

        style.configure(
            "Tlabel",
        )

        style.configure(
            "button.TFrame",
            background="#fcc200",
        )

        style.configure(
            "display.TFrame",
            background="maroon",
        )


def main():
    """Run AGV Control GUI"""
    GUI().mainloop()


if __name__ == "__main__":
    main()
