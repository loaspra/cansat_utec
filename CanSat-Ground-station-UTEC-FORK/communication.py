import random
import serial
import serial.tools.list_ports


class Communication:
    baudrate = ''
    portName = ''
    dummyPlug = False
    ports = serial.tools.list_ports.comports()
    ser = serial.Serial()
    startlat = -12.408921 # -12.135400 
    startlon = -69.202937 # -77.022095
    increase =   0.000500


    def __init__(self):
        self.baudrate = 9600
        print("the available ports are (if none appear, press any letter): ")
        for port in sorted(self.ports):
            # obtener la lista de puertos: https://stackoverflow.com/a/52809180
            print(("{}".format(port)))
        self.portName = input("write serial port name (ex: /dev/ttyUSB0): ")
        try:
            self.ser = serial.Serial(self.portName, self.baudrate)
        except serial.serialutil.SerialException:
            print("Can't open : ", self.portName)
            self.dummyPlug = True
            print("Dummy mode activated")

    def close(self):
        if(self.ser.isOpen()):
            self.ser.close()
        else:
            print(self.portName, " it's already closed")

    def getData(self):
        if(self.dummyMode == False):
            value = self.ser.readline()  # read line (single value) from the serial port
            decoded_bytes = str(value[0:len(value) - 2].decode("utf-8"))
            value_chain = decoded_bytes.split(",")
            print(value_chain)
        else:
                                # lon              lat                  vel                            temp                                 height                          press                              hum                       yawpitchroll/ax ay az       para  cam  trans                 
            value_chain = [self.startlon] + [self.startlat] + [random.random()*(3-0) + 0] + [random.random()*(38-16) + 16] + random.sample(range(280, 300), 1)  + [random.random()*(12-5) + 5] + random.sample(range(80, 100), 1) + random.sample(range(0, 20), 6) + [0] + [1] + [1]
            self.startlat = self.startlat + self.increase
            self.startlon = self.startlon + self.increase
            print(value_chain)
        return value_chain

    def isOpen(self):
        return self.ser.isOpen()

    def dummyMode(self):
        return self.dummyPlug
