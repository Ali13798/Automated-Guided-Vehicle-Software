class AgvStyles:
    """Includes the style specifications of the AGV COntrol GUI"""

    FONT_SIZE = 20
    PADDING = 10

    @staticmethod
    def config_styles(style) -> None:
        style.configure(
            "TButton",
            background="#fcc200",
            font=(None, AgvStyles.FONT_SIZE),
            padding=AgvStyles.PADDING,
        )
        style.configure(
            "control.TButton",
            width=3,
        )

        # Configure styles - Labels
        style.configure(
            "TLabel",
            font=(None, AgvStyles.FONT_SIZE),
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
        style.configure(
            "canvas.TFrame",
            # background="green",
        )

        # Configure styles - Textbox
        style.configure(
            "TEntry",
            font=(None, AgvStyles.FONT_SIZE),
            foreground="#5e0009",
        )

        # Configure styles - Scales
        style.configure(
            "TScale",
            background="#5e0009",
        )

        return style
