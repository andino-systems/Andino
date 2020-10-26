import platform
import socket
import threading
import time
import atexit
from threading import Thread
from time import sleep
from gpiozero import Button, DigitalOutputDevice, Device

if __name__ == "__main__":
    HOST = ""
    PORT = 1997

    # --- SETUP FOR GPIO --- #

    # Create Fake pins if running on windows
    if platform.system() == "Windows":
        from gpiozero.pins.mock import MockFactory

        Device.pin_factory = MockFactory()

    pin_input_1 = 13
    pin_input_2 = 19

    pin_relay_1 = 5
    pin_relay_2 = 6
    pin_relay_3 = 12

    pin_power_fail = 18

    # Simulate fake inputs if running on windows
    if platform.system() == "Windows":
        def simulate():
            print("Running on Windows - Mock Pins generated")
            pin1 = Device.pin_factory.pin(pin_input_1)
            while 1:
                pin1.drive_high()
                sleep(0.01)
                pin1.drive_low()
                sleep(0.99)

 
        simulator = Thread(target=simulate)
        simulator.start()

    outRel1 = DigitalOutputDevice(pin_relay_1, active_high=True, initial_value=False)
    outRel2 = DigitalOutputDevice(pin_relay_2, active_high=True, initial_value=False)
    outRel3 = DigitalOutputDevice(pin_relay_3, active_high=True, initial_value=False)

 
    class InOutStatus:
        input1 = 0
        input2 = 0
        input3 = 0
        rel1 = 0
        rel2 = 0
        rel3 = 0

        message_counter = 0
        send = 3000  # send all xx ms

        polling_time = 0.005  # min_sig length ms
        debounce_time = 0.005  # intervall between state changes ms

        def reset_func(self):
            self.input1 = 0
            self.input2 = 0
            self.input3 = 0
            self.rel1 = 0
            self.rel2 = 0
            self.rel3 = 0
            self.message_counter = 0
            self.send = 3000

        def send_func(self, x):
            self.send = x

        def inc_input_1(self):
            self.input1 = (self.input1 + 1) % 0xFFFF

        def inc_input_2(self):
            self.input2 = (self.input2 + 1) % 0xFFFF

        def get_and_inc_message_counter(self):
            x = self.message_counter
            self.message_counter = (self.message_counter + 1) % 0xFFFF
            return x

        def set_relay(self, x):
            relay_nr = x[3]
            relay_goal_state = x[5]
            if relay_nr == "1":
                if relay_goal_state == "1":
                    outRel1.on()
                    self.rel1 = 1
                elif relay_goal_state == "0":
                    outRel1.off()
                    self.rel1 = 0
            elif relay_nr == "2":
                if relay_goal_state == "1":
                    outRel2.on()
                    self.rel2 = 1
                elif relay_goal_state == "0":
                    outRel2.off()
                    self.rel2 = 0
            elif relay_nr == "3":
                if relay_goal_state == "1":
                    outRel3.on()
                    self.rel3 = 1
                elif relay_goal_state == "0":
                    outRel3.off()
                    self.rel3 = 0
            return x

        def pulse_relay(self, x):
            # We need a thread for this or else we will get no messages while pulsing
            def pulse_thread_code(this, rel, time_sec):
                print(rel)
                print(duration)
                if rel == 1:
                    outRel1.on()
                    this.rel1 = 1
                    time.sleep(time_sec)
                    outRel1.off()
                    this.rel1 = 0
                elif rel == 2:
                    outRel2.on()
                    this.rel2 = 1
                    time.sleep(time_sec)
                    outRel2.off()
                    this.rel2 = 0
                elif rel == 3:
                    outRel3.on()
                    this.rel3 = 1
                    time.sleep(time_sec)
                    outRel3.off()
                    this.rel3 = 0

            relay_nr = x[3]
            duration = int(x[4:])
            rpu = Thread(target=pulse_thread_code, args=(self, relay_nr, duration))
            rpu.start()
            return x

 
    status = InOutStatus()
    btnInput1 = Button(pin_input_1, hold_time=status.polling_time, bounce_time=status.debounce_time)
    btnInput2 = Button(pin_input_2, hold_time=status.polling_time, bounce_time=status.debounce_time)
    btnInput1.when_pressed = status.inc_input_1
    btnInput2.when_pressed = status.inc_input_2

    # --- Handle Input coming from the FSM
    def web_input(input_string):
        if input_string.startswith("status"):
            print(status.message_counter)
            return ":" + format(status.get_and_inc_message_counter(), 'x') + "{" + format(status.input1,
                                                                                          'x') + "," + format(
                status.input2, 'x') + "," + format(status.input3, 'x') + "}{" + format(status.rel1, 'x') + "," + format(
                status.rel2, 'x') + "," + format(status.rel3, 'x') + "}"

        # RESET( Restart controller)
        elif input_string.startswith("reset"):
            status.reset_func()
            print("resetting")
            return "reset"

        # INFO( print settings)
        elif input_string.startswith("info"):
            return "Running on AndinoIO Http Server"

        # HARD(Hardware, 0 = noShield, 1 = 1DI2DO, 2 = 3DI, 3 = 5DI)
        elif input_string.startswith("hard"):
            return "AndinoIO"

        # SEND 5000      ( send all xxx ms )
        elif input_string.startswith("send"):
            status.send_func(int(input_string[5:]))
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
            return status.set_relay(input_string)

        # RPU1|2|3 1000      ( pulse relais 1 for nnn ms )
        elif input_string.startswith("rpu"):
            return status.pulse_relay(input_string)

        else:
            return "404 Not found"

 
    # --- USP PowerFail ---

    def shutdown():
        if platform.system() != "Windows":
            from os import system
            system('sudo shutdown now')

 
 
 
 
    # --- SETUP FOR THE WEB SERVER ---

    def send_thread(sock, client_address):
        try:
            while True:
                sleep(status.send / 1000)
                sock.send((web_input("status") + "\n").encode('utf-8'))
        except ConnectionAbortedError:
            print("{} - Client Disconnected - Can't send status".format(client_address))
        except ConnectionResetError:
            print("{} - Connection reset".format(client_address))
        except BrokenPipeError:
            print("{} - Connection Lost While Writing".format(client_address))
        finally:
            t.join()
            connection.close()

 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        def closeSock():
            print("Shutting Down")
            s.close()
        atexit.register(closeSock)
        s.bind((HOST, PORT))
        s.listen()
        web_socket = s
        while True:
            connection, address = s.accept()
            print("connected: {}".format(address))
            t = threading.Thread(target=send_thread, args=(connection, address))
            t.daemon = True
            t.start()
            try:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    print("{}: {}".format(address, data.decode('ascii')))
                    connection.send((web_input(data.decode('ascii'))).encode('ascii'))
            except ConnectionAbortedError:
                print("{} - Client Disconnected".format(address))

            except ConnectionResetError:
                print("{} - Connection reset".format(address))
            finally:
                t.join()
                connection.close()
