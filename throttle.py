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

    def __init__(self, port, max_pressure, baud=9600, timeout=1,
                 line_term='\r\n', debug=False):
        self.debug = debug      # Output serial communication to console
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.line_term = line_term
        self.max_pressure = float(max_pressure)
        self.ser = None
        self.Connect()  # Disable to decouple connection from object creation

    def __send(self, cmd):
        ''' Internal function to format and send serial commands '''
        if self.ser:
            if self.debug:
                print("> " + cmd)
            self.ser.write((cmd + self.line_term).encode())

    def __read(self):
        ''' Internal function to read and return serial responses '''
        if self.ser:
            ret = self.ser.readline().decode().rstrip()
            if self.debug:
                print("< " + ret)
        else:
            raise serial.SerialException("Throttle: Can't read; not connected")
        return ret

    def Connect(self, port=None, baud=None, timeout=None, line_term=None):
        ''' Can allow serial connection after object creation '''
        if self.ser:
            raise serial.SerialException("Throttle: Already connected")
        self.port = port or self.port
        self.baud = baud or self.baud
        self.timeout = timeout or self.timeout
        self.line_term = line_term or self.line_term
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)

    def Disconnect(self):
        ''' Close serial connection '''
        if self.ser:
            self.ser.close()
        self.ser = None

    def Open(self, soft=False, step_size=None, step_delay=None):
        ''' Open throttle valve, optionally in steps'''
        if soft:
            self.Move(90.0, soft, step_size, step_delay)
        else:
            self.__send('O')

    def Close(self, soft=False, step_size=None, step_delay=None):
        ''' Close throttle valve, optionally in steps '''
        if soft:
            self.Move(0.0, soft, step_size, step_delay)
        else:
            self.__send('C')

    def softOpen(self, step_size=None, step_delay=None):
        ''' Open throttle valve, optionally in steps'''
        self.Open(90.0, True, step_size, step_delay)

    def getPosition(self):
        self.__send('R6')
        return float(self.__read()[1:])

    def setPosition(self, pos):
        ''' Overrides pressure control until pressure setpoint is given '''
        self.__send('P' + str(float(pos)))

    def getPressureSetpoint(self):
        self.__send('R1')
        # Use [2:] if dipswitch 2 is on
        return float(self.__read()[1:]) * self.max_pressure / 100.0

    def setPressure(self, setpoint):
        ''' Resumes analog pressure control if previously overriden '''
        self.__send('A')
        # Use 'S1' if dipswitch 2 is on
        self.__send('S' + str(100.0 * float(setpoint) / self.max_pressure))

    def Hold(self):
        ''' Hold throttle at current position until further instructions '''
        self.__send('H')

    def Move(self, target, soft=False, step_size=1.0, step_delay=1.0):
        ''' Move the throttle valve to target position.
            If soft == True, valve will move to target in steps defined by
            step_size and step_delay. '''
        if soft:
            # Move to target position in steps
            p = self.getPosition()
            while abs(target - p) > 1.1:
                step = target - p           # Calculate next position
                if abs(step) >= step_size:
                    step = step * step_size / abs(step)
                next_pos = p + step
                self.setPosition(next_pos)    # Move to next position
                while abs(next_pos - p) > 1.1:
                    p = self.getPosition()
                    time.sleep(0.1)
                time.sleep(step_delay)      # Wait at current step
                p = self.getPosition()
        else:
            # Move directly to target postion
            self.setPosition(target)

    def getGain(self):
        ''' Returns gain value in percent '''
        self.__send('R2')
        return float(self.__read()[1:])

    def setGain(self, gain):
        self.__send('G' + float(gain))

    def getLead(self):
        ''' Returns lead value in percent '''
        self.__send('R3')
        return float(self.__read()[1:])

    def setLead(self, lead):
        self.__send('L' + float(lead))

    # @property
    # def gain(self):
    #     ''' Returns gain value in percent '''
    #     self.__send('R2')
    #     return float(self.__read()[1:])
    #
    # @gain.setter
    # def gain(self, v):
    #     self.__send('G' + float(v))
    #
    # @property
    # def lead(self):
    #     ''' Returns lead value in percent '''
    #     self.__send('R3')
    #     return float(self.__read()[1:])
    #
    # @lead.setter
    # def lead(self, v):
    #     self.__send('L' + float(v))
    #
    # @property
    # def position(self):
    #     self.__send('R6')
    #     return float(self.__read()[1:])
    #
    # @position.setter
    # def position(self, pos):
    #     ''' Overrides pressure control until pressure setpoint is given '''
    #     self.__send('P' + str(float(pos)))
    #
    # @property
    # def pressure(self):
    #     self.__send('R1')
    #     # Use [2:] if dipswitch 2 is on
    #     return float(self.__read()[1:]) * max_pressure / 100.0
    #
    # @pressure.setter
    # def pressure(self, setpoint):
    #     ''' Resumes analog pressure control if previously overriden '''
    #     self.__send('A')
    #     # Use 'S1' if dipswitch 2 is on
    #     self.__send('S' + str(100.0 * setpoint / max_pressure))


if __name__ == '__main__':
    throttle = Throttle('COM5', 1000, debug=True)
    # throttle.Connect()
    throttle.Move(65.0, True)
    throttle.getPressureSetpoint()
    throttle.setPressure('0.0')
    throttle.Disconnect()
