#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import sys
from typing import Dict, Tuple, List
if sys.platform == "linux":
    import busio
    import adafruit_ssd1306
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class andino_io_oled:
    def __init__(self):
        """
        Initializes a new OLED instance
        The Images will be shown on windows but no i2c devices will be opened
        """
        self.WIDTH = 128
        self.HEIGHT = 64
        if sys.platform == "linux":
            self.i2c = busio.I2C(3, 2)
            self.display = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, self.i2c)
            self.display.fill(0)
            self.display.show()

        self.padding = -2
        self.config: (str, str) = ("21", None)
        self.text = [['AndinoPy', 'running']]
        if sys.platform == "linux":
            self.font_path = r"/usr/share/fonts/truetype/FIRACODE.TTF"
        else:
            self.font_path = r"C:\Windows\Fonts\Consolas\consola.ttf"
        self.fonts = {"default": ImageFont.load_default()}
        for i in [60, 30, 40, 21, 20, 16, 14, 8]:
            self.fonts[f"font{i}"] = ImageFont.truetype(self.font_path, i)
        self.modes: Dict[str, Tuple[List[int], str]] = {  # top diffs,font
            "10": ([0], "font60"),  # 1 Line, 3 Chars mode
            "11": ([20], "font30"),  # 1 Line, 4 Chars mode
            "20": ([0, 35], "font30"),  # 2 Line, 6 Chars
            "21": ([5, 40], "font21"),  # 2 Line, 9 Chars
            "30": ([2, 24, 46], "font20"),  # 3 Line, 9 Chars
            "31": ([2, 27, 52], "font16"),  # 3 Line, 12 Chars
            "40": ([1, 17, 34, 51], "font14"),  # 4 Line, 14 Chars
            "60": ([3, 13, 23, 33, 43, 53], "font8")  # 6 Line
        }

    def set_mode(self, col1: str, col2: str = None):
        """
        When using two columns beware only half the chars are avaiable
        "10":  1 Line, 3 Chars mode
        "11":  1 Line, 4 Chars mode
        "20":  2 Line, 6 Chars
        "21":  2 Line, 9 Chars
        "30":  3 Line, 9 Chars
        "31":  3 Line, 12 Chars
        "40":  4 Line, 14 Chars
        "60":  6 Line
        :param col1: see above
        :param col2: see above
        """
        self.config = (col1, col2)

    def set_text(self, text: [[str]]):
        """
        Set TExt on the display
        :param text: [["col1 row1","col1 row2"],["col2 row2"...]]
        """
        self.text = text
        self.display_text()

    def display_text(self):
        """
        Displays the text set in self.text
        """
        if sys.platform == "linux":
            self.display.fill(0)
            self.display.show()
        my_image = Image.new('1', (self.WIDTH, self.HEIGHT))
        draw = ImageDraw.Draw(my_image)
        for j in range(len(self.config)):
            if self.config[j] is not None:
                offset = 0.5*self.WIDTH*j
                row, font = self.modes[self.config[j]]
                font = self.fonts[font]

                for i in range(len(row)):
                    text = text = self.text[j][i]
                    draw.text(xy=(offset, self.padding + row[i]), font=font, text=text, fill=255)
                    # print(my_image.tobytes())
        if sys.platform == "linux":
            self.display.image(my_image)
            self.display.show()
        else:
            my_image.show()


if __name__ == "__main__":
    display = andino_io_oled()
    display.display_text()
