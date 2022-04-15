from time import sleep_ms
from _thread import start_new_thread
from sys import stdin, exit
from utime import sleep


#
# self.bufferSTDIN() function to execute in parallel on second Pico RD2040 thread/processor
#

class USB(object):
    def __init__(self):
        #
        # global variables to share between both threads/processors
        #
        self.bufferSize = 1024  # size of circular self.buffer to allocate
        self.buffer = [' '] * self.bufferSize  # circuolar incomming USB serial data self.buffer (pre fill)
        self.bufferEcho = True  # USB serial port echo incooming characters (True/False)
        self.bufferNextIn, self.bufferNextOut = 0, 0  # pointers to next in/out character in circualr self.buffer
        self.terminateThread = False  # tell 'self.bufferSTDIN' function to terminate (True/False)

    def bufferSTDIN(self):
        while True:  # endless loop
            if self.terminateThread:  # if requested by main thread ...
                break  # ... exit loop
            self.buffer[self.bufferNextIn] = stdin.read(1)  # wait for/store next byte from USB serial
            if self.bufferEcho:  # if echo is True ...
                print(self.buffer[self.bufferNextIn], end='')  # ... output byte to USB serial
            self.bufferNextIn += 1  # bump pointer
            if self.bufferNextIn == self.bufferSize:  # ... and wrap, if necessary
                self.bufferNextIn = 0

    #
    # instantiate second 'background' thread on RD2040 dual processor to monitor and self.buffer
    # incomming data from 'stdin' over USB serial port using ‘self.bufferSTDIN‘ function (above)
    #
    # self.bufferSTDINthread = start_new_thread(self.bufferSTDIN, ())

    #
    # function to check if a byte is available in the self.buffer and if so, return it
    #
    def getBytebuffer(self):
        if self.bufferNextOut == self.bufferNextIn:  # if no unclaimed byte in self.buffer ...
            return ''  # ... return a null string
        n = self.bufferNextOut  # save current pointer
        self.bufferNextOut += 1  # bump pointer
        if self.bufferNextOut == self.bufferSize:  # ... wrap, if necessary
            self.bufferNextOut = 0
        return self.buffer[n]  # return byte from self.buffer

    #
    # function to check if a line is available in the self.buffer and if so return it
    # otherwise return a null string
    #
    # NOTE 1: a line is one or more bytes with the last byte being LF (\x0a)
    #      2: a line containing only a single LF byte will also return a null string
    #
    def getLineBuffer(self):
        if self.bufferNextOut == self.bufferNextIn:  # if no unclaimed byte in self.buffer ...
            return ''  # ... RETURN a null string

        n = self.bufferNextOut  # search for a LF in unclaimed bytes
        while n != self.bufferNextIn:
            if self.buffer[n] == '\x0a':  # if a LF found ...
                break  # ... exit loop ('n' pointing to LF)
            n += 1  # bump pointer
            if n == self.bufferSize:  # ... wrap, if necessary
                n = 0
        if n == self.bufferNextIn:  # if no LF found ...
            return ''  # ... RETURN a null string

        line = ''  # LF found in unclaimed bytes at pointer 'n'
        n += 1  # bump pointer past LF
        if n == self.bufferSize:  # ... wrap, if necessary
            n = 0

        while self.bufferNextOut != n:  # BUILD line to RETURN until LF pointer 'n' hit

            if self.buffer[self.bufferNextOut] == '\x0d':  # if byte is CR
                self.bufferNextOut += 1  # bump pointer
                if self.bufferNextOut == self.bufferSize:  # ... wrap, if necessary
                    self.bufferNextOut = 0
                continue  # ignore (strip) any CR (\x0d) bytes

            if self.buffer[self.bufferNextOut] == '\x0a':  # if current byte is LF ...
                self.bufferNextOut += 1  # bump pointer
                if self.bufferNextOut == self.bufferSize:  # ... wrap, if necessary
                    self.bufferNextOut = 0
                break  # and exit loop, ignoring (i.e. strip) LF byte
            line = line + self.buffer[self.bufferNextOut]  # add byte to line
            self.bufferNextOut += 1  # bump pointer
            if self.bufferNextOut == self.bufferSize:  # wrap, if necessary
                self.bufferNextOut = 0
        return line  # RETURN unclaimed line of input

    #
    # main program begins here ...
    #
    # set 'inputOption' to either  one byte ‘BYTE’  OR one line ‘LINE’ at a time. Remember, ‘self.bufferEcho’
    # determines if the background self.buffering function ‘self.bufferSTDIN’ should automatically echo each
    # byte it receives from the USB serial port or not (useful when operating in line mode when the
    # host computer is running a serial terminal program)
    #
    # start this MicroPython code running (exit Thonny with code still running) and then start a
    # serial terminal program (e.g. putty, minicom or screen) on the host computer and connect
    # to the Raspberry Pi Pico ...
    #
    #    ... start typing text and hit return.
    #
    #    NOTE: use Ctrl-C, Ctrl-C, Ctrl-D then Ctrl-B on in the host computer terminal program
    #           to terminate the MicroPython code running on the Pico
    #
    def start(self):
        try:
            inputOption = 'LINE'  # get input from self.buffer one BYTE or LINE at a time
            while True:

                if inputOption == 'BYTE':  # NON-BLOCKING input one byte at a time
                    buffCh = self.getBytebuffer()  # get a byte if it is available?
                    if buffCh:  # if there is...

                        print(buffCh, end='')  # ...print it out to the USB serial port

                elif inputOption == 'LINE':  # NON-BLOCKING input one line at a time (ending LF)
                    buffLine = self.getLineBuffer()  # get a line if it is available?
                    if buffLine:  # if there is...
                        print(buffLine)  # ...print it out to the USB serial port

                sleep(0.1)

        except KeyboardInterrupt:  # trap Ctrl-C input
            terminateThread = True  # signal second 'background' thread to terminate
            exit()


usb = USB()
input_msg = None
bufferSTDINthread = start_new_thread(usb.bufferSTDIN, ())
cnt = 0
while True:
    cnt += 1
    if cnt > 50:
        cnt = 0
        print('ping')

    inputOption = 'LINE'  # get input from self.buffer one BYTE or LINE at a time
    if inputOption == 'BYTE':  # NON-BLOCKING input one byte at a time
        buffCh = usb.getBytebuffer()  # get a byte if it is available?
        if buffCh:  # if there is...
            print('BYTE')
            # print(buffCh, end='')  # ...print it out to the USB serial port

    elif inputOption == 'LINE':  # NON-BLOCKING input one line at a time (ending LF)
        buffLine = usb.getLineBuffer()  # get a line if it is available?
        if buffLine:  # if there is...
            print('LINE')  # ...print it out to the USB serial port

    sleep_ms(50)
