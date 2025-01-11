import traceback

from Arduino import Arduino
import serial.tools.list_ports

DEBUG = True


class ArduinoController:
    def __init__(self, baud=57600, port=None):
        self.baud = baud
        self.port = port
        self.board = None

        self._slicer_main = 0
        self._slicer = [0.0, 0.0, 0.0, 0.0]
        self._slicer_num = len(self._slicer) + 1

        self._buttons = [False, False, False, False]
        self._buttons_previous_state = [False, False, False, False]
        self._buttons_size = len(self._buttons)

    def start(self):
        try:
            self.board = serial.Serial()
            self.board.baudrate = self.baud
            self.board.port = self.port
            self.board.timeout = 3
            self.board.open()
        except Exception:
            print(traceback.format_exc())

    def update(self):
        if not self.board.is_open:
            return

        result = ""
        try:
            result = self.board.readline().decode("utf-8").strip()
        except UnicodeDecodeError:
            print("Error decoding characters...")
            return

        if DEBUG:
            print(result)

        result_splited = result.split("|")
        if len(result_splited) != self._slicer_num + self._buttons_size:
            print("Discarting received values...")
            return

        for i in range(0, self._slicer_num + self._buttons_size):
            try:
                if i == 0:
                    self._slicer_main = int(result_splited[i]) * 0.01
                elif i < self._slicer_num:
                    self._slicer[i - 1] = int(result_splited[i]) * 0.01
                elif i < self._slicer_num + self._buttons_size:
                    self._buttons[i - self._slicer_num] = int(result_splited[i])

            except ValueError:
                print(f"Discarting received slider {i} value...")

    def close(self):
        if self.board:
            self.board.close()

    def reconnect(self, port):
        self.close()
        self.port = port
        self.board = Arduino(port)

    def get_slicer_gain(self, id):
        assert id < 4
        return self._slicer[id]

    def get_slicer_main_gain(self):
        return self._slicer_main

    def is_opened(self):
        return self.board.is_open
