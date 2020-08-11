# MKS 135 butterfly valve RS-232 control
# Dave Matthews, Swift Coat Inc, August 2020

# TODO: support Python context manager

import serial
import time


class Throttle(object):
    ''' MKS 135F butterfly valve, RS-232 control
        Requires straight-thru serial cable, not null modem as described in
        manual.
        Expects DIP switches to be set as follows:
        1: On
        2: Off
        3: On
        4: On
        5: Off
        6: Off
        7: Off
        8 - 10 independent
    '''

    def __init__(self, port=None, baud=None, timeout=1, line_term='\r\n',
                 debug=False):
        ''' Init and optionally save parameters for serial connection later '''
        self.debug = debug          # Output serial communication to console
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.line_term = line_term
        self.ser = None

    def connect(self, port=None, baud=None, timeout=None, line_term=None):
        ''' Allows serial connection after object creation '''
        if self.ser:
            raise serial.SerialException("Already connected!")
        self.port = port or self.port
        self.baud = baud or self.baud
        self.timeout = timeout or self.timeout
        self.line_term = line_term or self.line_term
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)

    def disconnect(self):
        ''' Close serial connection '''
        if self.ser:
            self.ser.close()
        self.ser = None

    def open(self, soft=False, step_size=None, step_delay=None):
        ''' Open throttle valve, optionally in steps'''
        if soft:
            self.move(90.0, soft, step_size, step_delay)
        else:
            self.__send('O')

    def close(self, soft=False, step_size=None, step_delay=None):
        ''' Close throttle valve, optionally in steps '''
        if soft:
            self.move(0.0, soft, step_size, step_delay)
        else:
            self.__send('C')

    def move(self, target, soft=False, step_size=1.0, step_delay=1.0):
        ''' Move the throttle valve to target position.
            If soft == True, valve will move to target in steps defined by
            step_size and step_delay. '''
        if soft:
            # Move to target position in steps
            p = self.position
            while abs(p - target) >= 0.1:
                step = target - p           # Calculate next position
                if abs(step) >= step_size:
                    step = step * step_size / abs(step)
                next_pos = p + step
                self.position = next_pos    # Move to next position
                while abs(p - next_pos) >= 0.1:
                    p = self.position
                    time.sleep(0.1)
                time.sleep(step_delay)      # Wait at current step
        else:
            # Move directly to target postion
            self.position = target

    @property
    def position(self):
        self.__send('R6')
        ret = self.__read()
        return float(ret[1:])

    @position.setter
    def position(self, pos):
        # TODO: Set to position control
        self.__send('P' + str(float(pos)))

    @property
    def pressure(self):
        self.__send('R1')
        ret = self.__read()
        return float(ret[1:])               # ret[2:] if dipswitch 2 is on

    @pressure.setter
    def pressure(self, setpoint):
        # TODO: Set to pressure control
        self.__send('S' + str(float(pos)))  # 'S1' if dipswitch 2 is on

    def __send(self, cmd):
        ''' Internal function to format and send serial commands '''
        if self.ser:
            print("> " + cmd)
            self.ser.write((cmd + self.line_terminator).encode())

    def __read(self):
        ''' Internal function to read and return serial responses '''
        if self.ser:
            ret = self.ser.readline().decode().rstrip()
            print("< " + ret)
        else:
            ret = None
        return ret


throttle = Throttle('COM5', 9600, 1)
throttle.connect()
throttle.move(0.0, True)
throttle.disconnect()
