# Test framework / DUT model for TAMK course

import os
import voltmeter
from time import sleep

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
        args = "--reset write {file_path} 0x{address:08x}".format(file_path=file_path, address=address)
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


class VoltMeterInterface(Interf):
    """ Interface for reading the voltage through Digilent AnalogDiscovery 2

    """
    def __init__(self):
        self.vm = voltmeter.VoltMeter()
        name = "VoltMeter at Digilent AnalogDiscovery 2 " + self.vm.get_version()
        super().__init__(name)

        ver = self.vm.get_version()
        print ("Digilent version " + ver)
        self.vm.open()
        self.vm.setup_acquisition()

    def read(self):
        return self.vm.meas_vdc(0)

    def write(self, string):
        raise RuntimeError("This interface is read-only")

    def __del__(self):
        pass
        self.vm.close()


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
        self.sleep = 0.05

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
        
