#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß

from typing import List, Callable
from socket import socket, AF_INET, SOCK_STREAM
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
        address: (str, int) = None
        _client_socket: socket = None
        _thread: Thread = None
        _parent_server: 'tcp_server' = None
        _running: bool = True
        _on_message: callable([str, socket]) = None

        def __init__(self, address: str, client_socket: socket,
                     parent_server, on_message: callable([str, 'client_handle'])):
            self.address = address
            self._client_socket = client_socket
            self._parent_server = parent_server
            self._on_message = on_message
            self._thread = Thread(target=self._receive_thread)
            self._thread.daemon = True
            andinopy_logger.debug(f"{self.address[0]}:{self.address[1]} connected")
            self._thread.start()

        def send_message(self, message):
            try:
                self._client_socket.send(message.encode('utf-8'))
            except Exception:
                self.remove()

        def _receive_thread(self):
            try:
                while self._running:
                    data = self._client_socket.recv(1024)
                    if not data:
                        break
                    data = data.decode('utf-8')
                    if self._on_message is not None:
                        self._on_message(data, self)
            finally:
                self.remove()

        def remove(self):
            andinopy_logger.debug(f"{self.address[0]}:{self.address[1]} disconnected")
            self._running = False
            self._client_socket.close()
            self._parent_server.clients.remove(self)

    # Network
    HOST: str = None
    PORT: int = None
    clients: List[client_handle] = []
    broadcast_timer: int = 0
    _running: bool = False
    _socket: socket = None
    _client_accept_thread: Thread = None
    _broadcast_thread: Thread = None

    # Custom functions
    on_message: callable([str, client_handle]) = None
    generate_broadcast: Callable[['tcp_server'], str] = None

    def __init__(self, host: str = "", port: int = 9999, on_message: callable([str, 'client_handle']) = print_message,
                 generate_broadcast: Callable[['tcp_server'], str] = broadcast_all_clients, broadcast_timer: int = 0):
        """
        Initialize a new TCP server which then should be customized
        :param host: An empty string means localhost
        :param port: The Port on which the server should be reachable
        """
        andinopy_logger.debug("TCP Server instance created")
        self.HOST = host
        self.PORT = port
        self.on_message = on_message
        self.generate_broadcast = generate_broadcast
        self.broadcast_timer = broadcast_timer

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
        self._client_accept_thread.join()
        self._broadcast_thread.join()
        self._socket.close()

    def send_to_all(self, message: str):
        for i in self.clients:
            i.send_message(message)

    def _accept_thread(self):
        andinopy_logger.debug("starting accept thread")
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.bind((self.HOST, self.PORT))
        self._socket.listen()
        while self._running:
            sock, address = self._socket.accept()
            self.clients.append(self.client_handle(address, sock, self, self.on_message))

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
