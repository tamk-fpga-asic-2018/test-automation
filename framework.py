# Test framework / DUT model for TAMK course

import os
import sys
from time import sleep
from dwfconstants import *
# import voltmeter

from helpers import error_handler

try:
    import serial
except ImportError:
    error_handler("PySerial not installed. Run 'python -m pip install pyserial'")


class Dut(object):
    def __init__(self, firmware, board, name):
        self.firmware = firmware
        self.board = board
        self.name = name

class ProgrammerWin(object):
    CLI_TOOL = "c:\\program files (x86)\\STMicroelectronics\\STM32 ST-LINK Utility\\ST-LINK Utility\\ST-LINK_CLI.exe"

    def write_firmware_and_verify(self, file_path, address):
        args = "-P \"{file_path}\" 0x{address:08x} ".format(file_path=file_path, address=address)
        self.execute(args)

    def reset_board(self):
        args = "-Rst"
        self.execute(args)

    def execute(self, args):
        cmd = ("\"{programmer}\" {args}".format(programmer=self.CLI_TOOL, args=args))
        os.system('"' + cmd + '"')

class ProgrammerLinux(object):
    CLI_TOOL= "/usr/local/bin/st-flash"

    def write_firmware_and_verify(self, file_path, address):
        args = "--reset write \"{file_path}\" 0x{address:08x}".format(file_path=file_path, address=address)
        self.execute(args)

    def reset_board(self):
        args = "reset"
        self.execute(args)

    def execute(self, args):
        cmd = ("{programmer} {args}".format(programmer=self.CLI_TOOL, args=args))
        os.system(cmd)

class Programmer(object):
    PROGRAMMER = {
        "nt": ProgrammerWin,
        "posix": ProgrammerLinux
    }

    def __init__(self):
        try:
            self.cli = self.PROGRAMMER[os.name]()
        except KeyError:
            raise OSError("Only Windows and Linux environments currently supported.")
        if not os.path.isfile(self.cli.CLI_TOOL):
            raise EnvironmentError("Required {cli} not installed or configuration is incorrect"
                                   .format(cli=self.cli.CLI_TOOL))


class Firmware(object):
    def __init__(self, name):
        if not os.path.isfile(name):
            error_handler("Firmware file {name} does not exist".format(name=name))
        self.name = name
        
    def write_to_dut(self, address=0x08000000):
        # STLINK cli
        file_path = os.path.abspath(self.name)
        programmer = Programmer()
        programmer.cli.write_firmware_and_verify(file_path=file_path, address=address)
        

class Board(object):
    def __init__(self, name):
        self.name = name
        self.interfaces = dict()
        self.default_interface = None

    def add_interface(self, interface_name, interface):
        self.interfaces[interface_name] = interface
    
    def set_default_interface(self, interface_name):
        self.default_interface = self.interfaces[interface_name]

    def reset(self):
        Programmer().cli.reset_board()
        

class Interf(object):
    """ Generic interface for accessing DUT

    """
    def __init__(self, name=None):
        if name is None:
            self.name = "Generic Interface"
        else:
            self.name = name
        
    def read(self):
        raise NotImplementedError("This function shall be implemented in the inherited interface.")

    def write(self, value):
        raise NotImplementedError("This function shall be implemented in the inherited interface.")

# FIXME Voltmeter task
# Idea: copy paste from voltmeter.py


class VoltMeter(Interf):
    """ Interface for reading the voltage through Digilent AnalogDiscovery 2

    """
    def __init__(self, freq = 10000000.0, n_of_samples = 4000):

        try:
            if sys.platform.startswith("win"):
                self.dwf = cdll.dwf
            elif sys.platform.startswith("darwin"):
                self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
            else:
                self.dwf = cdll.LoadLibrary("libdwf.so")
        except:
            print ("Can't load DWF library. Digilent not usable.")

        self.n_of_samples = n_of_samples
        self.freq = freq

        #declare ctype variables
        self.hdwf = c_int()
        self.sts = c_byte()
        self.IsEnabled = c_bool()
        self.rgdSamples = (c_double * self.n_of_samples)()


        name = "VoltMeter at Digilent AnalogDiscovery 2 " + self.get_version()
        super().__init__(name)
        # TODO add content

    def open(self):
        """ Open the device

        """
        print ("Opening first device")
        self.dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))

        if self.hdwf.value == hdwfNone.value:
            raise IOError("failed to open Analog Discovery 2 device")

    def close(self,):
        if self.hdwf is None:
            self.dwf.FDwfDeviceCloseAll()
        else:
            self.dwf.FDwfDeviceClose(self.hdwf)

    
    def setup_acquisition(self):
        """Set up acquisition

        """
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(self.freq))
        self.dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(self.n_of_samples))
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(0), c_bool(True))
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(0), c_double(5))
        self.dwf.FDwfAnalogInChannelOffsetSet(self.hdwf, c_int(0), c_double(2.5))
        # pvoltsrange=c_double()
        # dwf.FDwfAnalogInChannelRangeGet(hdwf, c_int(0), byref(pvoltsrange))
        # print(pvoltsrange)

        # wait at least 2 seconds for the offset to stabilize
        sleep(2)


    def read(self, channel=0):
        """Measure average DC voltage
        """

        # begin acquisition
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_bool(False), c_bool(True))
        # print ("   waiting to finish")

        while True:
            self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(1), byref(self.sts))
            # print ("STS VAL: " + str(sts.value) + "STS DONE: " + str(DwfStateDone.value))
            if self.sts.value == DwfStateDone.value :
                break
            sleep(0.1)
        # print ("Acquisition finished")

        self.dwf.FDwfAnalogInStatusData(self.hdwf, channel, self.rgdSamples, self.n_of_samples) # get data

        dc = sum(self.rgdSamples)/len(self.rgdSamples) # average
        return dc

    def write(self, string):
        raise RuntimeError("This interface is read-only")

    def get_version(self):
        """ Returns DWF version as string

        """
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)
        return str(version.value.decode("utf-8"))

    def __del__(self):
        self.close()


class Serial(Interf):
    def __init__(self, port):
        name = "Serial=" + port
        super().__init__(name)

        self.serial_args = {
            'port': port,
            'baudrate': 115200,
            'bytesize': 8,
            'parity': 'N',
            'stopbits': 1,
            'timeout': 1
        }
        self.sleep = 0.1

        try:
            self._connection = serial.Serial(**self.serial_args)
        except serial.serialutil.SerialException:
            error_handler("Can't open serial port {port}".format(port=self.serial_args['port']))
        
    def read(self):
        """ Read serial buffer
        
        Returns list of integers

        """
        result = []
        self._connection.flush()
        while self._connection.in_waiting > 0:
            data = self._connection.read(self._connection.in_waiting)
            result.extend(data)
        return result


    def write(self, string):
        """ Write string to serial interface.
        
        Args:
            string (str): string to be sent to serial interface
    
        """
        sleep(self.sleep)
        self._connection.write(string.encode('ascii'))
        while self._connection.out_waiting > 0:
            sleep(self.sleep)
        sleep(self.sleep)
        
