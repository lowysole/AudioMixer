import traceback

from Arduino import Arduino
import serial.tools.list_ports

import ButtonController

DEBUG = True


class ArduinoController:
    def __init__(self, baud=57600):
        self.baud = baud
        self.port = self.get_port()
        self.board = None

        self._slicer_main = 0
        self._slicer = [0.0, 0.0, 0.0, 0.0]
        self._slicer_num = len(self._slicer) + 1

        self._buttons = [False, False, False, False]

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
            if not self.reconnect():
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
        if len(result_splited) != self._slicer_num + ButtonController.NUM_BUTTONS:
            print("Discarting received values...")
            return

        for i in range(0, self._slicer_num + ButtonController.NUM_BUTTONS):
            try:
                if i == 0:
                    self._slicer_main = int(result_splited[i]) * 0.01
                elif i < self._slicer_num:
                    self._slicer[i - 1] = int(result_splited[i]) * 0.01
                elif i < self._slicer_num + ButtonController.NUM_BUTTONS:
                    self._buttons[i - self._slicer_num] = int(result_splited[i])

            except ValueError:
                print(f"Discarting received slider {i} value...")

    def close(self):
        if self.board:
            self.board.close()

    def reconnect(self):
        try:
            self.port = self.get_port()
            self.board = Arduino(self.board.baudrate, self.port)
            self.board.open()
            return True
        except Exception:
            print(traceback.format_exc())
            return False

    def get_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "USB-SERIAL CH340" in port.description:
                print(f"Arduino found on Port: {port.device}")
                return port.device

        print("Arduino device not found.")

    def get_slicer_gain(self, id):
        assert id < 4
        return self._slicer[id]

    def get_slicer_main_gain(self):
        return self._slicer_main

    def get_button_value(self, id):
        assert id < ButtonController.NUM_BUTTONS
        return self._buttons[id]

    def set_button_value(self, id, value):
        assert id < ButtonController.NUM_BUTTONS
        self._buttons[id] = value

    def is_opened(self):
        if self.board:
            return self.board.is_open
        else:
            return False

    def send_board_button_mode(self, values):
        assert len(values) == ButtonController.NUM_BUTTONS
        self._send_command(
            f"BUTTON_MODE|{values[0]}|{values[1]}|{values[2]}|{values[3]}"
        )

    def send_board_button_init(self, values):
        assert len(values) == ButtonController.NUM_BUTTONS
        self._send_command(
            f"BUTTON_INIT|{values[0]}|{values[1]}|{values[2]}|{values[3]}"
        )

    def _send_command(self, message):
        self.board.write(message)
