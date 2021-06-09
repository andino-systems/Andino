#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import sys
from typing import Callable, Optional
from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
import time
from threading import Thread
from andinopy import andinopy_logger


def print_message(message: str, client: 'tcp_server.client_handle'):
    print(f"{client.address[0]}:{client.address[1]}: {message}")


def broadcast_all_clients(tcp_server_instance: 'tcp_server'):
    return f"These clients are connected:" \
           f" {','.join(i.address[0] + ':' + i.address[1] for i in tcp_server_instance.clients)}"


class tcp_server:
    class client_handle:

        def __init__(self, address: str, client_socket: socket,
                     parent_server, on_message: callable([str, 'client_handle'])):
            self._running: bool = True
            self.address: (str, int) = address
            self._client_socket: socket = client_socket
            self._parent_server: 'tcp_server' = parent_server
            self._on_message: callable([str, socket]) = on_message
            self._thread: Thread = Thread(target=self._receive_thread)
            self._thread.daemon = True

            self._thread.start()

        def send_message(self, message):
            try:
                self._client_socket.send(message.encode(self._parent_server.encoding))
            except OSError:
                self.remove()

        def send_line(self, message: str):
            self.send_message(message + "\n")

        def _receive_thread(self):
            andinopy_logger.debug(f"{self.address[0]}:{self.address[1]} connected")
            try:
                while self._running:
                    data = self._client_socket.recv(1024)
                    if not data:
                        break
                    data = data.decode(self._parent_server.encoding)
                    if self._on_message is not None:
                        self._on_message(data, self)
            except OSError:
                andinopy_logger.debug("client closed before reading was finihsed")

        def remove(self):
            andinopy_logger.debug(f"{self.address[0]}:{self.address[1]} disconnected")
            self._running = False
            self._client_socket.shutdown(SHUT_WR)
            self._client_socket.close()
            self._parent_server.clients.remove(self)

    def __init__(self, host: str = "", port: int = 9999, on_message: callable([str, 'client_handle']) = print_message,
                 generate_broadcast: Callable[['tcp_server'], str] = broadcast_all_clients, broadcast_timer: int = 0,
                 encoding: str = "ascii"):
        """
        Initialize a new TCP server which should then be customized
        :param host: An empty string means localhost
        :param port: The Port on which the server should be reachable
        """
        # Network

        self.encoding = "ascii"
        self.clients = []
        self.broadcast_timer: int = 0
        self._running: bool = False
        self._socket: socket = socket(AF_INET, SOCK_STREAM)
        self._client_accept_thread: Optional[Thread] = None
        self._broadcast_thread: Optional[Thread] = None

        # Custom functions
        self.on_message: callable([str, 'client_handle']) = None
        self.generate_broadcast: Callable[['tcp_server'], str]

        self.HOST: str = host
        self.PORT: int = port
        self.on_message = on_message
        self.generate_broadcast = generate_broadcast
        self.broadcast_timer = broadcast_timer
        self.encoding = encoding
        andinopy_logger.debug("TCP Server instance created")

    def start(self):
        self._running = True
        self._client_accept_thread = Thread(target=self._accept_thread)
        self._client_accept_thread.daemon = True
        self._broadcast_thread = Thread(target=self._broadcast_thread_function)
        self._broadcast_thread.daemon = True
        self._client_accept_thread.start()
        self._broadcast_thread.start()

    def stop(self):
        self._running = False
        for i in self.clients:
            i.remove()
        self._socket.close()
        self._client_accept_thread.join(1)
        self._broadcast_thread.join(1)

    def send_to_all(self, message: str):
        for i in self.clients:
            i.send_message(message)

    def send_line_to_all(self, message: str):
        for i in self.clients:
            i.send_line(message)

    def _accept_thread(self):
        andinopy_logger.debug("starting accept thread")

        if not sys.platform.startswith("win"):
            from socket import SO_REUSEADDR, SOL_SOCKET
            self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._socket.bind((self.HOST, self.PORT))
        self._socket.listen()
        try:
            while self._running:
                sock, address = self._socket.accept()
                self.clients.append(self.client_handle(address, sock, self, self.on_message))
        except OSError:
            andinopy_logger.debug("Server closed while waiting for connections")
        finally:
            self._socket.close()

    def _broadcast_thread_function(self):
        andinopy_logger.debug("starting send status thread")
        while self._running:
            if self.broadcast_timer > 0:
                time.sleep(self.broadcast_timer / 1000)
                if len(self.clients) > 0:
                    message = self.generate_broadcast(self)
                    andinopy_logger.debug(f"{len(self.clients)} clients connected - broadcast message is {message}")
                    for client in self.clients:
                        client.send_message(message)
            else:
                time.sleep(1)
