from threading import Lock, Thread
import time
import traceback

from Arduino import Arduino
from Logger import logger, logger_arduino
import serial.tools.list_ports

import ButtonController


class ArduinoController:
    def __init__(self, baud=57600):
        self.baud = baud
        self.port = self.get_port()
        self.board = None
        self._board_is_open = False

        self._slicer_main = 0
        self._slicer = [0.0, 0.0, 0.0, 0.0]
        self._slicer_num = len(self._slicer) + 1

        self._buttons = [False, False, False, False]

        self._command_queue = []
        self._mutex = Lock()

        self.thread = Thread(target=self._update_command_queue)

    def start(self):
        try:
            self.board = serial.Serial()
            self.board.baudrate = self.baud
            self.board.port = self.port
            self.board.timeout = 3
            self.board.open()
        except Exception:
            logger.error(traceback.format_exc())
            return

        self._board_is_open = True
        self.thread.start()

    def update(self):
        if not self._board_is_open:
            if self.thread.is_alive():
                self.thread.join()
            if not self.reconnect():
                return

        result = ""
        try:
            result = self.board.readline().decode("utf-8").strip()
        except UnicodeDecodeError:
            logger.warning("Error decoding characters...")
            return
        except serial.SerialException:
            self._board_is_open = False
            return

        logger_arduino.log(result)

        result_splited = result.split("|")
        if len(result_splited) != self._slicer_num + ButtonController.NUM_BUTTONS:
            logger.warning("Discarting received values...")
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
                logger.warning(f"Discarting received slider {i} value...")

    def _update_command_queue(self):
        while self._board_is_open:
            for command in self._command_queue:
                with self._mutex:
                    self._send_command(command)
                    self._command_queue.pop(0)
                time.sleep(2)

            time.sleep(0.1)

    def close(self):
        if self.board:
            self.board.close()

        if self.thread.is_alive():
            self.thread.join()

    def reconnect(self):
        try:
            self.port = self.get_port()
            self.board = Arduino(self.board.baudrate, self.port)
            self.board.open()

            self._board_is_open = True
            self.thread.start()
            return True
        except Exception:
            logger.error(traceback.format_exc())
            return False

    def get_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "USB-SERIAL CH340" in port.description:
                logger.info(f"Arduino found on Port: {port.device}")
                return port.device

        logger.info("Arduino device not found.")

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
        return self._board_is_open

    def send_board_button_mode(self, values):
        assert len(values) == ButtonController.NUM_BUTTONS
        self._add_command_to_queue(
            f"BUTTON_MODE|{int(values[0][1].value)}|{int(values[1][1].value)}|{int(values[2][1].value)}|{int(values[3][1].value)}"
        )

    def send_board_button_init(self, values):
        assert len(values) == ButtonController.NUM_BUTTONS
        self._add_command_to_queue(
            f"BUTTON_INIT|{values[0]}|{values[1]}|{values[2]}|{values[3]}"
        )

    def send_board_preset(self, value):
        self._add_command_to_queue(f"PRESET|{value}")
        return

    def _send_command(self, message):
        if self.board:
            if not message.endswith("\n"):
                message += "\n"
            self.board.write(message.encode("utf-8"))

    def _add_command_to_queue(self, message):
        with self._mutex:
            self._command_queue.append(message)
