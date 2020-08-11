# import queue
import serial
import time
# import threading


# class Plc(object):
#     def __init__(self, n_switches=23):
#         self.n_switches = n_switches
#         self.switches = ['0'] * n_switches
#         self.read_q = queue.Queue()
#         self.write_q = queue.Queue()
#         self.com = threading.Thread(target=self.com_loop)
#         self.com.start()
#
#     def com_loop(self):
#         with serial.Serial('COM3', 115200, timeout=0.1) as plc:
#             plc.write(b'y')
#             while self.running:
#                 # self.read_q.put(plc.readline())
#                 plc.write(self.write_q.get().encode() + '\r\n')
#                 time.sleep(0.1)

# plc = Plc()
# time.sleep(5)


delay = 0.1
n_switches = 22
with serial.Serial('COM4', 115200, timeout=1) as plc:
    def write(cmd):
        print('> ' + cmd)
        plc.write(('<{}>\r\n'.format(cmd)).encode())

    def read():
        print(plc.readline())

    time.sleep(delay)
    read()
    write('y')
    time.sleep(delay)
    read()
    while True:
        write('2,' + '0,' * n_switches)
        time.sleep(delay)
        write('2,' + '1,' * n_switches)
        time.sleep(delay)
        for i in range(n_switches):
            states = ['0'] * n_switches
            states[i] = '1'
            cmd = '2,' + ','.join(states)
            write(cmd)
            time.sleep(delay)
