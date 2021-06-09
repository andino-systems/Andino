import time

from andinopy.tcp.andino_tcp import andino_tcp

if __name__ == "__main__:
    server = andino_tcp()
    try:
        andino_tcp.start()
        while 1:
            time.sleep(1)
    except Exception as e:
        andino_tcp.stop()