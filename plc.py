# TODO: Find connected Arduino automatically

import argparse
import serial
from time import sleep


def quit(msg=None):
    if msg:
        print(msg)
    print("\nExiting...")
    exit(0)


parser = argparse.ArgumentParser(
    description="Convert text file to serial commands.")
parser.add_argument('port',
    help="Serial port where Arduino is connected (ex: COM3)")
parser.add_argument('file', nargs='?', type=open,
    help="txt file containing one serial command per line. " +
         "Leave blank for interactive mode.")
parser.add_argument('-b', '--baud', type=int, default=115200,
    help="Serial connection baud rate, default = 115200")
parser.add_argument('-d', '--delay', type=float, default='0.2',
    help="Delay between commands, in seconds")
parser.add_argument('-l', '--loop', nargs='?',
    help="If present, will run text file or self-test as loop indefinitely. " +
         "If followed by a number N, will exit after N seconds.")
# parser.add_argument('-n', '--n_switches', type=int,
#     help="Number of switches")
parser.add_argument('-s', '--selftest', nargs='?',
    help="Ignore other arguments besides PORT and run self-test routine. " +
         "If followed by a number N, will exit after N seconds.")
parser.add_argument('-t', '--timeout', type=float, default=1.0,
    help="Serial connection timeout in seconds, default = 1.0")
args = parser.parse_args()


# with serial.Serial(args.port, args.baud, timeout=args.timeout) as plc:
with Object() as plc:

    def write(cmd):
        print('> ' + cmd)
        # plc.write(('<{}>\r\n'.format(cmd)).encode())

    def read():
        # print('< ' + plc.readline().decode())
        print("read")

    # Connect to Arduino
    sleep(args.delay)
    read()
    write('y')
    sleep(args.delay)
    read()
    sleep(args.delay)
    running = True
    t0 = time.time()

    # Self-test
    while args.selftest:
        write('2,' + '0,' * args.n_switches)
        sleep(args.delay)
        write('2,' + '1,' * args.n_switches)
        sleep(args.delay)
        for i in range(args.n_switches):
            switches = ['0'] * args.n_switches
            switches[i] = '1'
            cmd = '2,' + ','.join(switches)
            write(cmd)
            sleep(args.delay)
        if isinstance(args.selftest, int) and args.selftest > time.time() - args.selftest:
            quit("\nSelf-test complete.")

    # File input
    if args.file:
        for line in args.file:
            write(line)
            sleep(args.delay)
        quit("\nFinished executing {}.".format(args.file))

    # Interactive mode
    cmd = ''
    while cmd != 'q':
        cmd = input()
        write(cmd)
