# test-automation
Test automation exercise

log1.txt -> tamk_1.bin
log2.txt -> tamk_2.bin
log3.txt -> tamk_3.bin
log4.txt -> tamk_4.bin


# Running the tests
Example:
```c:\python36-32\python.exe test_cases.py my_firmware.bin```

Script will always try to re-write the firmware to DUT.

If firmware is not passed as argument, default firmware defined in the script is 
used instead.

## test_cases.py
* test cases as functions
* test sequencer
* environment configuration

## framework.py
* DUT model and APIs

## helpers.py
* helper functions for framework and test cases

## voltmeter.py
* stand-alone voltmeter using Analog Discovery 2

## dwfconstants.py
* required by voltmeter.py


