#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
# import pytest
# import andinopy.andino_tcp
import sys
import time
import unittest
from unittest import TestCase

import andinopy.base_devices.andinoio


class test_andino_io(TestCase):

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_3input_status(self):
        import gpiozero
        from gpiozero.pins.mock import MockFactory
        gpiozero.Device.pin_factory = MockFactory()
        andino = andinopy.base_devices.andinoio.andinoio(input_pull_up=[False for _ in range(6)])
        inputs = andino._input_pins
        andino.start()
        for i in inputs:
            pin = gpiozero.Device.pin_factory.pin(i)
            pin.drive_high()
        time.sleep(0.1)
        self.assertEqual([1 for _ in range(len(andino.Inputs))], andino.get_input_statuses())

        for i in inputs:
            pin = gpiozero.Device.pin_factory.pin(i)
            pin.drive_low()
        time.sleep(0.1)
        self.assertEqual([0 for _ in range(len(andino.Inputs))], andino.get_input_statuses())

        andino.stop()
        del andino

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_2input_counter(self):
        import gpiozero
        from gpiozero.pins.mock import MockFactory
        gpiozero.Device.pin_factory = MockFactory()
        andino = andinopy.base_devices.andinoio.andinoio()
        inputs = andino._input_pins
        andino.input_pull_up = [False for _ in range(len(inputs))]
        andino.start()
        self.assertEqual([i.counter for i in andino.Inputs], [0 for _ in range(len(andino.Inputs))])
        expected_low = 100
        for _ in range(expected_low):
            for i in inputs:
                pin = gpiozero.Device.pin_factory.pin(i)
                pin.drive_high()
                pin.drive_low()
        self.assertEqual([expected_low for _ in range(len(andino.Inputs))], [i.counter for i in andino.Inputs])
        for i in range(len(andino.Inputs)):
            andino.reset_counter(i)
        self.assertEqual([i.counter for i in andino.Inputs], [0 for _ in range(len(andino.Inputs))])
        expected_high = 10000

        for _ in range(expected_high):
            for i in inputs:
                pin = gpiozero.Device.pin_factory.pin(i)
                pin.drive_high()
                pin.drive_low()
        self.assertEqual([i.counter for i in andino.Inputs], [expected_high for _ in range(len(andino.Inputs))])
        andino.stop()
        del andino

    def test_0relay_pulse(self):
        import gpiozero
        from gpiozero.pins.mock import MockFactory
        if sys.platform != "linux":
            gpiozero.Device.pin_factory = MockFactory()
        andino = andinopy.base_devices.andinoio.andinoio()
        andino.start()
        try:
            for i in range(len(andino.outRel)):
                andino.pulse_relays(i, 3000)
                time.sleep(0.5)
                self.assertEqual(andino.outRel[i].value, 1)
                time.sleep(3)
                self.assertEqual(andino.outRel[i].value, 0)
        finally:
            andino.stop()

    def test_1relays(self):
        import gpiozero
        from gpiozero.pins.mock import MockFactory
        if sys.platform != "linux":
            gpiozero.Device.pin_factory = MockFactory()
        andino = andinopy.base_devices.andinoio.andinoio()
        andino.start()
        for i in range(len(andino.outRel)):
            andino.set_relay(i, 1)
            self.assertEqual(andino.outRel[i].value, 1)
            andino.set_relay(i, 0)
            self.assertEqual(andino.outRel[i].value, 0)

        for i in range(len(andino.outRel)):
            andino.pulse_relays(i, 2)
            self.assertEqual(andino.outRel[i].value, 1)
        time.sleep(2.1)
        for i in range(len(andino.outRel)):
            self.assertEqual(andino.outRel[i].value, 0)
        andino.stop()
        del andino
