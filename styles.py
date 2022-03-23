FONT_SIZE = 20
PADDING = 5


class AgvStyles:
    @staticmethod
    def config_styles(style):
        style.configure(
            "TButton",
            background="#fcc200",
            font=(None, FONT_SIZE),
            padding=PADDING,
        )
        style.configure(
            "control.TButton",
            width=3,
        )

        # Configure styles - Labels
        style.configure(
            "TLabel",
            font=(None, FONT_SIZE),
            background="#5e0009",
            foreground="white",
        )

        # Configure styles - Frames
        style.configure(
            "TFrame",
            background="#5e0009",
        )
        style.configure(
            "display.TFrame",
        )
        style.configure(
            "welcome.TFrame",
        )
        style.configure(
            "waypoint.TFrame",
        )

        # Configure styles - Textbox
        style.configure(
            "TEntry",
            font=(None, FONT_SIZE),
            foreground="green",
        )

        return style
