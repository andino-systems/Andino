#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import os
import sys
import time
import socket
import unittest
from typing import List

import andinopy.tcp.simpletcp
import andinopy.tcp.andino_tcp
from unittest import TestCase

from andinopy.tcp.io_x1_emulator import x1_emulator


class TcpClient:

    def __init__(self, Address: str, Port: int, timeout: int = 5):
        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.server_connection = Address, Port

    def connect(self) -> bool:
        self.socket.connect(self.server_connection)
        return True

    def stop(self):
        self.socket.close()

    def send(self, message) -> bool:
        self.socket.sendall(message.encode())
        return True

    def send_with_response(self, message, expected) -> bool:
        self.socket.sendall(message.encode())
        amount_received = 0
        amount_expected = len(expected)
        received = ""
        while amount_received < amount_expected:
            data = self.socket.recv(16)
            amount_received += len(data)
            received += data.decode()
        if received == expected:
            return True
        return False

    def receive_message(self):
        return self.socket.recv(1024).decode()


class test_tcp_server(TestCase):
    def test_receive(self):
        # tracemalloc.start()
        port = 9999
        server_message = ""

        def on_message(message: str, _):
            nonlocal server_message
            server_message = message

        server = andinopy.tcp.simpletcp.tcp_server(port=port, on_message=on_message)
        server.start()
        client = TcpClient('localhost', port)
        try:
            assert (client.connect())
            for i in range(10):
                test_message = f"test {i}"
                client.send(test_message)
                time.sleep(0.1)
                self.assertEqual(test_message, server_message)

        finally:
            server.stop()
            client.stop()
            self.assertEqual(server._running, False)
        # tracemalloc.stop()

    def test_tcp_broadcast(self):
        port = 9998

        test_message = "broadcast"
        server = andinopy.tcp.simpletcp.tcp_server(port=port,
                                                   generate_broadcast=lambda x: test_message,
                                                   broadcast_timer=1)
        client = TcpClient('localhost', port, )
        try:
            server.start()

            assert (client.connect())
            result = client.receive_message()
            self.assertEqual(result, test_message)
        finally:
            server.stop()
            client.stop()

    def test_answer(self):
        port = 9997

        def on_message(message: str, handle: andinopy.tcp.simpletcp.tcp_server.client_handle):
            handle.send_message(message)

        try:
            server = andinopy.tcp.simpletcp.tcp_server(port=port, on_message=on_message)
            server.start()
            client = TcpClient('localhost', port)
            assert (client.connect())
            for i in range(10000):
                test_message = f"test {i}"
                self.assertEqual(client.send_with_response(test_message, test_message), True)
        finally:
            client.stop()
            server.stop()


class test_andino_tcp(TestCase):
    port_number = 10000

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_1broadcast(self):
        import gpiozero
        from gpiozero.pins.mock import MockFactory
        gpiozero.Device.pin_factory = MockFactory()
        port = 8999
        andino_tcp = andinopy.tcp.andino_tcp.andino_tcp("io", port)
        client = TcpClient('localhost', port, )
        self.assertIsInstance(andino_tcp.x1_instance, x1_emulator)
        inputs = andino_tcp.x1_instance.io._input_pins
        relays = andino_tcp.x1_instance.io._relay_pins
        for i in andino_tcp.x1_instance.io.Inputs:
            i.pull_up = False

        andino_tcp.start()
        client.connect()
        try:
            expected_low = 100
            for _ in range(expected_low):
                for i in inputs:
                    pin = gpiozero.Device.pin_factory.pin(i)
                    pin.drive_high()
                    pin.drive_low()

            receive = client.receive_message()
            self.assertEqual(":0000{64,64,64,64,64,64}{0,0,0,0,0,0}\n", receive)
        finally:
            andino_tcp.stop()
            client.stop()

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_2relays(self):
        import gpiozero
        from gpiozero.pins.mock import MockFactory
        gpiozero.Device.pin_factory = MockFactory()
        port = 9995
        andino_tcp = andinopy.tcp.andino_tcp.andino_tcp("io", port)
        client = TcpClient('localhost', port, )
        inputs = andino_tcp.x1_instance.io._input_pins
        relays = andino_tcp.x1_instance.io._relay_pins
        andino_tcp.x1_instance.io.input_pull_up = [False for _ in range(len(inputs))]

        andino_tcp.start()
        client.connect()
        try:
            expect = "REL? 1\n"
            client.send(expect)
            receive = client.receive_message()
            print(receive)
            self.assertEqual(expect, receive)

            for i in range(len(relays)):
                message = f"REL{i + 1} 1\n"
                client.send(message)
                time.sleep(0.1)
                self.assertEqual(andino_tcp.x1_instance.io.outRel[i].value, 1)
                receive = client.receive_message()
                self.assertEqual(message, receive)
            time.sleep(andino_tcp.tcpserver.broadcast_timer)
            receive = client.receive_message()
            print(receive)
            self.assertTrue(receive.endswith("{1,1,1}\n"))
        finally:
            andino_tcp.stop()
            client.stop()

    def test_pulsing(self):
        if not sys.platform.startswith("linux"):
            import gpiozero
            from gpiozero.pins.mock import MockFactory
            gpiozero.Device.pin_factory = MockFactory()
        port = 9995
        andino_tcp = andinopy.tcp.andino_tcp.andino_tcp("io", port)
        inputs = andino_tcp.x1_instance.io._input_pins
        relays = andino_tcp.x1_instance.io._relay_pins
        client = TcpClient('localhost', port, )
        andino_tcp.start()
        client.connect()
        try:
            expect = "REL? 1\n"
            client.send(expect)
            receive = client.receive_message()
            self.assertEqual(expect, receive)

            # Relay pulsing working?
            for i in range(len(relays)):
                message = f"RPU{i + 1} 5000\n"
                client.send(message)
                time.sleep(0.2)
                # self.assertEqual(andino_tcp.x1_instance.io.outRel[i].value, 1)
                receive = client.receive_message()
                self.assertEqual(message, receive)
            receive = client.receive_message()
            self.assertTrue(receive.endswith("{1,1,1}\n"))
            time.sleep(andino_tcp.tcpserver.broadcast_timer)
            receive = client.receive_message()
            self.assertTrue(receive.endswith("{0,0,0}\n"))
        finally:
            andino_tcp.stop()
            client.stop()

    def test_files(self):
        directory = os.path.dirname(__file__)
        for folder in os.listdir(directory):
            folder_path = os.path.join(directory, folder)
            if os.path.isdir(folder_path):
                with self.subTest(folder):
                    in_path = os.path.join(folder_path, "out.txt")
                    out_path = os.path.join(folder_path, "in.txt")
                    self.assertTrue(os.path.isfile(in_path))
                    self.assertTrue(os.path.isfile(out_path))
                    in_file = open(in_path, "r")
                    out_file = open(out_path, "r")
                    try:
                        result = self.exec_test(in_file.read())
                        expected = out_file.read().splitlines()
                        self.assertEqual(expected, result)
                    finally:
                        in_file.close()
                        out_file.close()

    def exec_test(self, input_file):
        port = self.port_number
        self.port_number += 1
        if not sys.platform.startswith("linux"):
            import gpiozero
            from gpiozero.pins.mock import MockFactory
            gpiozero.Device.pin_factory = MockFactory()
        andino_tcp = andinopy.tcp.andino_tcp.andino_tcp("io", port)
        client = TcpClient('localhost', port, )
        output = []

        def receive_answer(recv_client):
            rec: List[str] = recv_client.receive_message().splitlines()
            for i in rec:
                if not i.startswith(":"):
                    return i
            return receive_answer(recv_client)

        try:
            andino_tcp.start()
            client.connect()
            lines = input_file.splitlines()
            for line in lines:
                if line:  # ignore empty lines
                    client.send(line)
                    output.append(receive_answer(client))
        finally:
            andino_tcp.stop()
            client.stop()
        return output
