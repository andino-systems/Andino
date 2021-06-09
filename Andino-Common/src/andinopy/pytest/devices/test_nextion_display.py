#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import time
from unittest import TestCase
from andinopy.base_devices.nextion_display import display


class test_nextion(TestCase):
    def test_0_global_var(self):
        nextion = display(serial_port="COM6")
        try:
            nextion.start()
            nextion.reset()
            recv = nextion.get_attr("testint")
            self.assertEqual(1, recv)

        finally:
            nextion.stop()

    def test_1_page(self):
        nextion = display(serial_port="COM6")
        try:
            nextion.start()
            nextion.reset()
            nextion.set_page("page1")
            self.assertTrue("y", input("do you see a page with a progressbar? y/n"))
        finally:
            nextion.stop()

    def test_2_button(self):
        btn = []

        def on_button_press(page, button_id, on_off):
            print(button_id)
            btn.append(button_id)

        my_display = display(serial_port="COM6")
        my_display.on_display_touch = on_button_press

        try:
            my_display.start()
            my_display.reset()
            my_display.set_page("page1")
            print("Please press Button pressme")
            while len(btn) == 0:
                time.sleep(0.01)
            self.assertEqual(1, 1)
        finally:
            my_display.stop()

    def test_3_output(self):
        my_display = display(serial_port="COM6")
        try:
            my_display.start()
            my_display.reset()
            my_display.set_page("page1")
            my_display.set_text("text1", "new text")
            self.assertEqual("y", input("Do you see the text 'new text'? y/n"))
        finally:
            my_display.stop()

    def test_4_colour(self):
        my_display = display(serial_port="COM6")
        try:
            my_display.start()
            my_display.reset()
            my_display.set_page("page1")
            my_display.set_text("text1", "new text")
            my_display.set_attr("text1", "pco", "255")
            self.assertEqual("y", input("Do you see the text 'new text' in blue color? y/n"))
        finally:
            my_display.stop()

    def test_5_slider_bar(self):
        my_display = display(serial_port="COM6")
        try:
            my_display.start()
            my_display.reset()
            my_display.set_page("page1")
            input("please put the value of the slider all the way to 100% - press enter when done")
            self.assertEqual(100, my_display.get_attr("slider.val"))
            input("please put the value of the slider all the way down to 0% - press enter when done")
        finally:
            my_display.stop()

    def test_6_progress_bar(self):
        my_display = display(serial_port="COM6")
        try:
            my_display.start()
            my_display.reset()
            my_display.set_page("page1")
            my_display.set_attr("progress", "val", "0")
            self.assertEqual("y", input("Is the progressbar empty? y/n"))
            my_display.set_attr("progress", "val", "100")
            self.assertEqual("y", input("Is the progressbar full? y/n"))
        finally:
            my_display.stop()
