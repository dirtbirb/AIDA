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
        1:  On
        2:  Off
        3:  On
        4:  On
        5:  Off
        6:  Off
        7:  Off
        8:  On
        9:  Depends on baratron
        10: Independent
    '''

    def __init__(self, max_pressure, port=None, baud=None, timeout=1,
                 line_term='\r\n', debug=False):
        ''' Init and optionally save parameters for serial connection later '''
        self.debug = debug          # Output serial communication to console
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.line_term = line_term
        self.max_pressure = max_pressure
        self.ser = None

    def __send(self, cmd):
        ''' Internal function to format and send serial commands '''
        if self.ser:
            if self.debug:
                print("> " + cmd)
            self.ser.write((cmd + self.line_terminator).encode())

    def __read(self):
        ''' Internal function to read and return serial responses '''
        if self.ser:
            ret = self.ser.readline().decode().rstrip()
            if self.debug:
                print("< " + ret)
        else:
            ret = None
        return ret

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

    def close(self, soft=False, step_size=None, step_delay=None):
        ''' Close throttle valve, optionally in steps '''
        if soft:
            self.move(0.0, soft, step_size, step_delay)
        else:
            self.__send('C')

    def hold(self):
        ''' Hold throttle at current position until further instructions '''
        self.__send('H')

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

    def open(self, soft=False, step_size=None, step_delay=None):
        ''' Open throttle valve, optionally in steps'''
        if soft:
            self.move(90.0, soft, step_size, step_delay)
        else:
            self.__send('O')

    @property
    def gain(self):
        ''' Returns gain value in percent '''
        self.__send('R2')
        return float(self.__read()[1:])

    @gain.setter
    def gain(self, v):
        self.__send('G' + float(v))

    @property
    def lead(self):
        ''' Returns lead value in percent '''
        self.__send('R3')
        return float(self.__read()[1:])

    @lead.setter
    def lead(self, v):
        self.__send('L' + float(v))

    @property
    def position(self):
        self.__send('R6')
        return float(self.__read()[1:])

    @position.setter
    def position(self, pos):
        ''' Overrides pressure control until pressure setpoint is given '''
        self.__send('P' + str(float(pos)))

    @property
    def pressure(self):
        self.__send('R1')
        # Use [2:] if dipswitch 2 is on
        return float(self.__read()[1:]) * max_pressure / 100.0

    @pressure.setter
    def pressure(self, setpoint):
        ''' Resumes analog pressure control if previously overriden '''
        self.__send('A')
        # Use 'S1' if dipswitch 2 is on
        self.__send('S' + str(100.0 * setpoint / max_pressure))


throttle = Throttle('COM5', 9600, 1, debug=True)
throttle.connect()
throttle.move(0.0, True)
throttle.disconnect()
