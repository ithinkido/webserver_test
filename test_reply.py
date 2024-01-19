import time
import serial
import serial.tools.list_ports
from serial import SerialException

try:
    tty = serial.Serial("/dev/ttyUSB0", 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 2.0)
    tty.write(b'IN;\033.R')
except SerialException as e:
    print("serial " + repr(e))

# read decimal number, followed by carriage return from plotter
def read_answer(tty):
    tty.write(b'IN;OI;\n')
    time.sleep(1)
    buf = bytearray()
    while True:
        c = tty.read(1)
        if not c:  # timeout
            print("not read INT")
        if c == b'\r':
            break
        buf += c
    print ("int reply" + str(buf))
    return int(buf)

        


def getReplySTR(tty,cmd):
    tty.write(b'OI;\n')
    reply = str(tty.read_until(b'\r').decode("utf-8"))
    if len(reply) > 1:
        print ("str reply" + reply)
        return reply
    else:
        print("not read STR")
        return   


while (1):

    time.sleep(1)
    getReplySTR(tty,"IN;OI;")
    
    # read_answer(tty)  
    # time.sleep(1)
