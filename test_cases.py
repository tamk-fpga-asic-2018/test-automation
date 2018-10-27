import os
import sys
import math

from time import sleep
from datetime import datetime

import framework

from helpers import *


def testcase_template(dut):
    """ Test case template

    Returns name and result as strings.
    
    """
    name = "Template for a test case"
    results = []  # Result array for sub-tasks

    # begin test content

    # end test content
    result = check_results(results)
    return name, result


def test_read_simple(dut):
    """ Simple reading test.

        Sets few PWM values. Resets DUT in between.

        Returns result "PASS" or "FAIL".

    """
    name = "Simple reading test for few individual values"

    # begin test content
    dut.board.reset()
    my_interface = dut.board.default_interface

    values = [0, 100, 500, 1000, 1500, 2000]
    results = []
    for sent in values:
        write_value(my_interface, sent)
        value = read_value(my_interface)

        value = remove_whitespace(value)
        if value != str(sent):
            print("incorrect value! Got: " + value + ", expected: " + str(sent))
            results.append("FAIL")
        else:
            print("OK! Got: " + value + ", expected: " + str(sent))
            results.append("PASS")
        sleep(2)
        dut.board.reset()

    result = check_results(results)
    # end test content
    return name, result


def test_read_range(dut):
    """ Simple reading test for value range.
        Sets a range of PWM values.

        Returns result "PASS" or "FAIL".

    """
    name = "Simple reading test for value range"
    results = []

    # begin test content
    dut.board.reset()
    for sent in range(0, 2001, 1):
        write_value(dut.board.default_interface, sent)
        value = read_value(dut.board.default_interface)
        
        value = remove_whitespace(value)
        
        if value != str(sent):
            print("incorrect value! Got: " + value + ", expected: " + str(sent))
            results.append("FAIL")
        else:
            print("OK! Got: " + value + ", expected: " + str(sent))
            results.append("PASS")

    # end test content
    result = check_results(results)
    return name, result


def test_invalid_values(dut):
    """ Test Serial API with invalid values.

        Returns "PASS" or "FAIL"

        TODO:
        1. Implement comparison of sent and expected value.
        2. Implement result determining according to specification.
        3. Simplify test case structure.

    """
    name = "Simple reading test for few invalid values"
    results = []
    # begin test content

    commands = ["1234\r",  # valid
                " 1234\r",
                "4321\r",
                "test\r",
                "0est\r",
                "tes1\r",
                "01234\r",
                "012345678\r",
                "0\r",  # valid
                "100\r",  # valid
                "500\r",  # valid
                "1000\r",  # valid
                "2000\r"  # valid
                ]

    for command in commands:
        my_interface.write(command)
        value = read_value(my_interface)
        # TODO: Compare to expected
        sleep(1)

    # end test content
    result = check_results(results)
    return name, result


def test_measure(dut):
    """ Simple voltage measurement test.

    Sets valid PWM values 0...2000. Reads voltage.
    Expects voltage to follow the changes of the PWM value.

    """
    name = "Voltage Measurement task"
    results = []
    # begin test content
    dut.board.reset()
    for sent in range(0, 2001, 1):
        write_value(dut.board.default_interface, sent)
        sleep(0.010)
        value = read_value(dut.board.interfaces["VoltMeter"])
        
        # Compare returned string of float to expected value
        # Expected value = (sent / 2000) * 3.3 (volts)
        # Problems with floating point comparison? -> use math.isclose() -> margins?
        expected = sent / 2000 * 3.3
        if not math.isclose(float(value), expected, rel_tol=0.02):
            print("incorrect value! Got: " + value + ", expected: " + str(expected))
            results.append("FAIL")
        else:
            print("OK! Got: " + value + ", expected: " + str(expected))
            results.append("PASS")
        

    # end test content

    result = check_results(results)
    return name, result


def test_sequence(dut, test_cases):
    """ Sequences tests and keeps a simple scoreboard for results.
    
    """
    results = {}

    print("*" * 78)
    for test in test_cases:
        print("BEGIN TEST: " + str(datetime.now()))
        name, result = test(dut)
        results[name] = result
        print("END TEST: " + str(datetime.now()))
        print((name + ": ").ljust(50) + "[" + result.upper() + "]")
        print("*" * 78)

    print("Tests completed.\nSummary:")

    for r in results:
        print((r + ": ").ljust(50) + "[" + results[r].upper() + "]")


def main():
    """ Brings up the board and starts the test sequence.
    
    """
    # ENVIRONMENT CONFIGURATION -------------------------------------------------

    serial_port = "COM10"     # serial_port = "/dev/ttyUSB0"
    firmware_file = "firmware/tamk_1.bin" # optionally overridden with command line argument
    board_name = "MyBoard"
    dut_name = "MyIndividualDut"

    # BOARD CONFIGURATION -------------------------------------------------------

    # Overrides the default firmware_file
    if len(sys.argv) > 1:
        firmware_file = sys.argv[1]

    myboard = framework.Board(board_name)

    # Interfaces
    myserial = framework.Serial(serial_port)
    myboard.add_interface("Serial", myserial)

    # TODO Voltmeter yet unfinished!
    myvoltmeter = framework.VoltMeterInterface()
    myboard.add_interface("VoltMeter", myvoltmeter)
    

    myboard.set_default_interface("Serial")

    sleep(1)

    # FIRMWARE CONFIGURATION ----------------------------------------------------
    myfirmware = framework.Firmware(firmware_file)
    myfirmware.write_to_dut()

    # DUT CONFIGURATION ---------------------------------------------------------
    mydut = framework.Dut(myfirmware, myboard, dut_name)
    interfaces_str = ''
    for i, iface_key in enumerate(mydut.board.interfaces.keys()):
        if i + 1 == len(mydut.board.interfaces.keys()):
            interfaces_str = interfaces_str + ' and '
        elif i > 0:
            interfaces_str = interfaces_str + ', '

        interfaces_str = interfaces_str + str(iface_key)

    print("Set-up: DUT: {dut} FW {firmware} on HW {board} connected with {interfaces}".
        format(
            dut=mydut.name,
            firmware=mydut.firmware.name,
            board=mydut.board.name,
            interfaces=interfaces_str
        )
    )

    # TEST CASES ----------------------------------------------------------------
    test_cases = [
        test_read_simple,
        test_read_range,
        test_invalid_values,
        test_measure
    ]

    test_sequence(mydut, test_cases)


if __name__ == "__main__":
    main()
