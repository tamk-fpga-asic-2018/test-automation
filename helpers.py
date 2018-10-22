# Helper functions for framework and test cases

import sys


def ints_to_string(intlist):
    """ Converts array of ints to character string.

    Args:
    
    """
    string = ""
    for digit in intlist:
        string += chr(digit)
    return string

def is_valid(value):
    """ Check if input value string contains integer between 0 and 2000.

    Args:
        value (str): Input value to be tested

    Returns:
        True if value is valid. False otherwise

    """
    stripped = value.rstrip("\r\n\0")
    if len(stripped) > 4:
        return False
    elif stripped.isdigit():
        if 0 <= int(stripped) <= 2000:
            return True
    else:
        return False

def write_value(interface, value):
    """ Write a valid value to interface.
    
    Args:
        interface: DUT interface
        value (int): Value to be written. Shall be 0...2000.

    """
    newline = "\r"

    if not isinstance(value, int):
        raise TypeError("Given value is not integer")
    if 0 <= value <= 2000:
        command = str(value) + newline
        interface.write(command)

        print("WRITE: " + str(command))
        
    else:
        raise ValueError("Given value is out of range")


def read_value(interface):
    """ Reads a value from interface

    Args:
        interface: Interface to be used

    Returns:
        read value as a string.

    """
    value = interface.read()
    if isinstance(value, list):
        string_value = ints_to_string(value)
    else:
        string_value = str(value)
    print("READ: " + string_value)
    return string_value


def remove_whitespace(input):
    """ Returns input string without whitespace characters.

    """
    return input.strip("\0\r\n ")


def check_results(results):
    """ Checks results array for failed items.

     Args:
         results (list): List of strings 'PASS' or 'FAIL'
     Returns:
         'PASS' if all results are 'PASS',
         'FAIL' if any result is 'FAIL',
         'UNKNOWN' if no results.

     """
    if len(results) == 0:
        result = "UNKNOWN"
    elif results.count("PASS") == len(results):
        result = "PASS"
    else:
        result = "FAIL"

    return result


def error_handler(msg):
    """ Error handling for Framework.

    """
    print("ERROR: " + msg)
    sys.exit(1)
