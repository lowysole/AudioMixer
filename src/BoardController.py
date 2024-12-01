from Arduino import Arduino
import serial.tools.list_ports

import traceback

class ArduinoController:
    def __init__(self, baud=9600, port=None):
        self.baud = baud
        self.port = port

        self.slicer_main = 0
        self.slicer_1 = 0
        self.slicer_2 = 0
        self.slicer_3 = 0
        self.slicer_4 = 0
        self.board = None


    def start(self):
        try:
            self.board = serial.Serial()
            self.board.baudrate = self.baud
            self.board.port = self.port
            self.board.timeout = 3
            self.board.open()
        except:
            print(traceback.format_exc())

    def update(self):
        if not self.board.is_open:
            return
        
        self.board.flush()
        result = str(self.board.readline())

        result = result[2:-5]

        print(result)
        result_splited = result.split('|')
        if len(result_splited) == 5:
            self.slicer_1 = result_splited[0]
            self.slicer_2 = result_splited[1]
            self.slicer_3 = result_splited[2]
            self.slicer_4 = result_splited[3]
            self.slicer_main = result_splited[4]


    def close(self):
        if self.board:
            self.board.close()

    def reconnect(self, port):
        self.close()
        self.port = port
        self.board = Arduino(port)


    def printPinInfo(self):
        print("---------------")
        print(f"Pin A0: {self.slicer_1}")
        print(f"Pin A1: {self.slicer_2}")
        print(f"Pin A2: {self.slicer_3}")
        print(f"Pin A3: {self.slicer_4}")
        print(f"Pin A4: {self.slicer_main}")



        