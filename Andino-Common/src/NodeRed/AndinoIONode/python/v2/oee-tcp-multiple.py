#     ___   ________  ________            _________    ______  _______
#   .'   `.|_   __  ||_   __  |          |  _   _  | .' ___  ||_   __ \
#  /  .-.  \ | |_ \_|  | |_ \_|  ______  |_/ | | \_|/ .'   \_|  | |__) |
#  | |   | | |  _| _   |  _| _  |______|     | |    | |         |  ___/
#  \  `-'  /_| |__/ | _| |__/ |             _| |_   \ `.___.'\ _| |_
#   `.___.'|________||________|            |_____|   `.____ .'|_____|
#  by Jakob Groß

import platform
import socket
import threading
import time
import atexit
from threading import Thread
from time import sleep
from gpiozero import Button, DigitalOutputDevice, Device


class tcpServer:

    class Client:
        address = None
        connection = None
        thread = None
        handler = None
        running = True

        def __init__(self, address, connection,handler):
            self.address = address
            self.connection = connection
            self.handler = handler
            self.thread = threading.Thread(target=self.receive_thread)
            self.thread.daemon = True
            print(f"{self.address[0]}:{self.address[1]} connected")
            self.thread.start()

        def send_message(self, message):
            try:
                self.connection.send(message.encode('utf-8'))
            except Exception:
                self.remove()


        def receive_thread(self):
            try:
                while self.running:
                    data = self.connection.recv(1024)
                    if not data:
                        break
                    data = data.decode('utf-8')
                    print(f"{self.address[0]}:{self.address[1]} sent: {data}")
                    response = self.handler.handle_web_input(data)
                    self.connection.send(response.encode('ascii'))
            finally:
                self.remove()

        def remove(self):
            print(f"{self.address[0]}:{self.address[1]} disconnected")
            self.running = False
            self.connection.close()
            self.handler.clients.remove(self)

    # Network
    HOST = None
    PORT = None
    clients = []
    running = False
    socket = None
    accept = None
    send = None

    # Pins
    input_pins = [13, 19, 16, 26, 20, 21]
    relay_pins = [5,6,12]
    pin_power_fail = 18

    # Handlers
    outRel = []
    btnInput = []

    # Stati
    inputs = [0, 0, 0, 0, 0, 0]
    relays = [0, 0, 0]
    message_counter = 0
    sendtimer = 3000  # send all xx ms
    polling_time = 0.005  # min_sig length ms
    debounce_time = 0.005  # intervall between state changes ms

    def __init__(self, host="", port=1997):
        print("TCP Server instance created")
        self.HOST = host
        self.PORT = port
        # Create Fake pins if running on windows
        if platform.system() == "Windows":
            self.simulate_windows()

        # init relays
        for pin in self.relay_pins:
            self.outRel.append(DigitalOutputDevice(pin, active_high=True, initial_value=False))

        # init inputs
        for i in range(len(self.input_pins)):
            tempbtn = Button(self.input_pins[i], hold_time=self.polling_time, bounce_time=self.debounce_time)
            tempbtn.when_pressed = lambda x=i: self.inc_input(x)
            self.btnInput.append(tempbtn)
        print(self.btnInput)

    def inc_input(self, i):
        self.inputs[i] = (self.inputs[i] + 1) % 0xFFFF

    def reset_func(self):
        for i in range(len(self.relays)):
            self.relays[i] = 0
            self.outRel[i].off()

        for i in range(len(self.inputs)):
            self.inputs[i] = 0

        self.message_counter = 0
        self.sendtimer = 3000

    def send_func(self, x):
        self.send = x

    def set_relay(self, x):
        relay_nr = int(x[3]) - 1
        relay_goal_state = int(x[5])
        if relay_goal_state == 1:
            self.outRel[relay_nr].on()
            self.relays[relay_nr] = 1
        elif relay_goal_state == 0:
            self.outRel[relay_nr].off()
            self.relays[relay_nr] = 0
        return x

    def pulse_relay(self, x):
        relay_nr = int(x[3] - 1)
        duration = int(x[5:])
        self.outRel[relay_nr].blink(on_time=duration, n=1, background=True)
        return x

    def get_and_inc_message_counter(self):
        x = self.message_counter
        self.message_counter = (self.message_counter + 1) % 0xFFFF
        return x

    def simulate_windows(self):
        from gpiozero.pins.mock import MockFactory
        Device.pin_factory = MockFactory()
        if platform.system() == "Windows":
            def simulate():
                print("Running on Windows - Mock Pins generated")
                pins = [Device.pin_factory.pin(x) for x in self.input_pins]
                pins[0].drive_high()
                while 1:
                    for pin in pins[1:]:
                        pin.drive_high()
                        sleep(0.01)
                        pin.drive_low()
                        sleep(0.99)

            simulator = Thread(target=simulate)
            simulator.start()

    def accept_thread(self):
        print("starting accept thread")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen()
        while self.running:
            sock, address = self.socket.accept()
            self.clients.append(self.Client(address, sock, self))

    def send_status_thread(self):
        print("starting send status thread")
        while self.running:
            if len(self.clients) > 0:
                message = self.generate_status()
                print(f"{len(self.clients)} clients connected - message is {message}")
                for client in self.clients:
                    client.send_message(message)
            time.sleep(int(self.sendtimer/1000))

    def generate_status(self):
        return f":{format(self.get_and_inc_message_counter(),'x')}" \
               f"{{{','.join(format(i,'x') for i in self.inputs)}}}" \
               f"{{{','.join(str(int(not i.value)) for i in self.btnInput)}}}" \
               f"{{{','.join(str(i) for i in self.relays)}}}"

    def start(self):
        self.running = True
        self.accept = threading.Thread(target=self.accept_thread)
        self.accept.daemon = True
        self.send = threading.Thread(target=self.send_status_thread)
        self.send.daemon = True
        self.accept.start()
        self.send.start()

    def stop(self):
        self.running = False
        self.accept.join()
        self.accept = None
        self.send.join()
        self.send = None
        self.socket.close()

    def handle_web_input(self,input_string):
        input_string = input_string.lower();
        # RESET( Restart controller)
        if input_string.startswith("reset"):
            self.reset_func()
            print("resetting")
            return "reset"

        # INFO( print settings)
        elif input_string.startswith("info"):
            return "Running on TCP Server"

        # HARD(Hardware, 0 = noShield, 1 = 1DI2DO, 2 = 3DI, 3 = 5DI)
        elif input_string.startswith("hard"):
            return "TCP Server"

        # SEND 5000      ( send all xxx ms )
        elif input_string.startswith("send"):
            self.send_func(int(input_string[5:]))
            return "send " + input_string[5:]

        elif input_string.startswith("poll"):
            #status.polling_time = float(input_string[5:])/1000
            #btnInput1.hold_time = status.polling_time
            #btnInput2.hold_time = status.polling_time
            #return "poll " + input_string[5:]
            return input_string

        elif input_string.startswith("debo"):
            #status.debounce_time = float(input_string[5:]) / 1000
            #btnInput1.bounce_time = status.debounce_time
            #btnInput2.bounce_time = status.debounce_time
            #return "debo " + input_string[5:]
            return input_string
        # POLL 10( Poll cycle in ms )
        # DEBO 3( Debounce n Scans stable to accept )
        # SKIP 3( Skip n Scans after pulse reconized )
        # EDGE1 | 0(count on Edge  HL or LH )

        # CHNG 0|1       ( send on Pin Change - carefull if many changes)
        # CNTR 0|1       ( Send counter, Default 1 otherwise on Pin States )
        elif input_string.startswith(
                "skip") or input_string.startswith("edge") or input_string.startswith(
            "chng") or input_string.startswith("cntr"):
            return input_string

        # REL1 0|1       ( set releais 1 to on or off )
        # REL2 0|1       ( set releais 2 to on or off )
        # REL3 0|1       ( set releais 3 to on or off )
        elif input_string.startswith("rel"):
            return self.set_relay(input_string)

        # RPU1|2|3 1000      ( pulse relais 1 for nnn ms )
        elif input_string.startswith("rpu"):
            return self.pulse_relay(input_string)

        else:
            return "404 Not found"


if __name__ == "__main__":
    server = tcpServer()
    server.start()
    atexit.register(server.stop)
    while 1:
        time.sleep(1)
