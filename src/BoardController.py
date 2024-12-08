from Arduino import Arduino
import serial.tools.list_ports

import traceback

class ArduinoController:
    def __init__(self, baud=9600, port=None):
        self.baud = baud
        self.port = port
        self.board = None
        
        self.slicer_main = 0
        self.slicer = [0.0,0.0,0.0,0.0]



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
        
        result = ''
        try:
            result = self.board.readline().decode('utf-8').strip()
            result = result[2:-5]
        except UnicodeDecodeError:
            print("Error decoding characters...")
            return

        print(result)
        result_splited = result.split('|')
        if len(result_splited) != 5:
            print("Discarting received values...")
            return
        
        for i in range(0,5):
            try:
                self.slicer[i] = int(result_splited[i])
            except ValueError:
                print(f"Discarting received slider {i} value...")

        # self.printPinInfo()


    def close(self):
        if self.board:
            self.board.close()

    def reconnect(self, port):
        self.close()
        self.port = port
        self.board = Arduino(port)


    def get_slicer_gain( self, id):
        assert ( id < 4)
        return self.slicer[id]
    

    def get_slicer_main_gain(self):
        return self.slicer_main
    

    def is_opened(self):
        return self.board.is_open


    def printPinInfo(self):
        print("---------------")
        print(f"Pin A0: {self.slicer[0]}")
        print(f"Pin A1: {self.slicer[1]}")
        print(f"Pin A2: {self.slicer[2]}")
        print(f"Pin A3: {self.slicer[3]}")
        print(f"Pin A4: {self.slicer_main}")

        