
class General():

    def __init__(self):

        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "gray": (125, 125, 125),
            "red": (255, 0, 0),
            "green" : (0, 255, 0),
            "blue" : (0, 0, 255),
            "purple" : (128, 0, 128),
            "yellow" : (255, 255, 0)

        }

        self.elevation_colors = {
            0: (46, 34, 22),    # Dark brown (lowest elevation)
            1: (69, 50, 27),    # Medium brown
            2: (92, 66, 32),    # Light brown
            3: (115, 82, 37),   # Tan
            4: (138, 98, 42),   # Light tan
            5: (161, 114, 47),  # Sandy yellow
            6: (184, 130, 52),  # Bright yellow
            7: (100, 150, 50),  # Light green
            8: (50, 120, 100),  # Teal (transition to blue)
            9: (30, 90, 150),   # Bright blue
            10: (10, 50, 100)   # Dark blue (highest elevation)
        }

        # parameters for the visuals
        self.world_size: int = 2500

