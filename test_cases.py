import os
import sys

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

        TODO:
        1. Implement comparison of sent and expected value.
        2. Implement result determining according to specification.

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
        # TODO implement missing logic here
        sent_str = str(sent)
        if value == sent_str:
            print("OK! Got: " + value + ", expected: " + sent_str)
            results.append("PASS")
        else:
            print("incorrect value! Got: " + value + ", expected: " + sent_str)
            results.append("FAIL")
        
        sleep(2)
        dut.board.reset()

    result = check_results(results)
    # end test content
    return name, result


def test_read_range(dut):
    """ Simple reading test for value range.
        Sets a range of PWM values.

        Returns result "PASS" or "FAIL".

        TODO:
        1. What goes wrong?
            if int != str 
        2. Fix it.

    """
    name = "Simple reading test for value range"
    results = []

    # begin test content
    dut.board.reset()
    for sent in range(0, 2001, 1):
        write_value(dut.board.default_interface, sent)
        value = read_value(dut.board.default_interface)

        sent_str = str(sent)
        if value != sent_str:
            print("incorrect value! Got: " + value + ", expected: " + sent_str)
            results.append("FAIL")
        else:
            print("OK! Got: " + value + ", expected: " + sent_str)
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

    dut.board.reset()
    my_interface = dut.board.default_interface

    testcase_list = list()
    testcase_list.append({"test": "1234", "expecting": "valid"})
    testcase_list.append({"test": " 1234", "expecting": "invalid"})
    testcase_list.append({"test": "4321", "expecting": "invalid"})
    testcase_list.append({"test": "test", "expecting": "invalid"})
    testcase_list.append({"test": "0est", "expecting": "invalid"})
    testcase_list.append({"test": "tes1", "expecting": "invalid"})
    testcase_list.append({"test": "01234", "expecting": "invalid"})
    testcase_list.append({"test": "012345678", "expecting": "invalid"})
    testcase_list.append({"test": "0", "expecting": "valid"})
    testcase_list.append({"test": "100", "expecting": "valid"})
    testcase_list.append({"test": "500", "expecting": "valid"})
    testcase_list.append({"test": "1000", "expecting": "valid"})
    testcase_list.append({"test": "2000", "expecting": "valid"})

    for testcase in testcase_list:
        print("WRITE: " + testcase["test"])
        my_interface.write(testcase["test"] + "\r")
        value = read_value(my_interface)

        if testcase["expecting"] == "valid":
            if value == testcase["test"]:
                print("OK!, Valid sent value, Got: " + value + ", expected: " + testcase["test"])
                results.append("PASS")
            else:
                print("incorrect value!, Valid sent value, Got: " + value + ", expected: " + testcase["test"])
                results.append("FAIL")

        elif testcase["expecting"] == "invalid":
            invalid_echo = testcase["test"][0:4]
            if value == invalid_echo:
                print("OK!, Invalid sent value, Got: " + value + ", expected: " + invalid_echo)
                results.append("PASS")
            else:
                print("incorrect value!, Invalid sent value, Got: " + value + ", expected: " + invalid_echo)
                results.append("FAIL")
        print()
        sleep(1)

    # end test content
    result = check_results(results)
    return name, result


def test_measure(dut):
    """ Simple voltage measurement test.

    Sets valid PWM values 0...2000. Reads voltage.
    Expects voltage to follow the changes of the PWM value.

    TODO:
    1. Implement voltmeter API re-using voltmeter.py functions. Add it to framework as a read-only interface.
    2. Re-use logic of other tests to make the functionality

    """
    name = "Voltage Measurement task"
    results = []
    # begin test content

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

    #serial_port = "/dev/cu.OmatSaadot1-FT9P9RH6"     # serial_port = "/dev/ttyUSB0"
    #serial_port = "/dev/cu.SLAB_USBtoUART" #vastaan otto ei tominut
    serial_port = "/dev/cu.usbmodem14121"   #Arduinon COM
    firmware_file = "./firmware/tamk_1.bin" # optionally overridden with command line argument
    board_name = "Nucleo-F446ZE"
    dut_name = "TAMK-dut"

    # BOARD CONFIGURATION -------------------------------------------------------

    # Overrides the default firmware_file
    if len(sys.argv) > 1:
        firmware_file = sys.argv[1]

    myboard = framework.Board(board_name)

    # Interfaces
    myserial = framework.Serial(serial_port)
    myboard.add_interface("Serial", myserial)


    # TODO Voltmeter yet unfinished!
    myvoltmeter = framework.VoltMeter()
    myboard.add_interface("VoltMeter", myvoltmeter)

    myboard.set_default_interface("Serial")

    sleep(1)

    # FIRMWARE CONFIGURATION ----------------------------------------------------
    myfirmware = framework.Firmware(firmware_file)
    myfirmware.write_to_dut()

    # DUT CONFIGURATION ---------------------------------------------------------
    mydut = framework.Dut(myfirmware, myboard, dut_name)

    print("Set-up: DUT: {dut} FW {firmware} on HW {board} connected with {interface}".
        format(
            dut=mydut.name,
            firmware=mydut.firmware.name,
            board=mydut.board.name,
            interface=mydut.board.default_interface.name
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
