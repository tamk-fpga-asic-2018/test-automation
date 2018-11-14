"""
   Based on DWF Python Example by Digilent, Inc.

"""

# from ctypes import *
from dwfconstants import *
import time
import sys

try:
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")
except:
    print ("Can't load DWF library. Digilent not usable.")

n_of_samples = 4000
freq = 10000000.0

#declare ctype variables
hdwf = c_int()
sts = c_byte()
IsEnabled = c_bool()
rgdSamples = (c_double*n_of_samples)()

def get_version():
    """ Returns DWF version as string

    """
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    return str(version.value.decode("utf-8"))

def open():
    """ Open the device

    """
    print ("Opening first device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        raise IOError("failed to open Analog Discovery 2 device")

def close(hdwf=None):
    if hdwf is None:
        dwf.FDwfDeviceCloseAll()
    else:
        dwf.FDwfDeviceClose(hdwf)

        
#set up acquisition
def setup_acquisition():
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(freq))
    dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(n_of_samples))
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
    dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(0), c_double(2.5))
    # pvoltsrange=c_double()
    # dwf.FDwfAnalogInChannelRangeGet(hdwf, c_int(0), byref(pvoltsrange))
    # print(pvoltsrange)

    # wait at least 2 seconds for the offset to stabilize
    time.sleep(2)


def meas_vdc(channel=0):
    # begin acquisition
    dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))
    # print ("   waiting to finish")

    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        # print ("STS VAL: " + str(sts.value) + "STS DONE: " + str(DwfStateDone.value))
        if sts.value == DwfStateDone.value :
            break
        time.sleep(0.1)
    # print ("Acquisition finished")

    dwf.FDwfAnalogInStatusData(hdwf, channel, rgdSamples, n_of_samples) # get data

    dc = sum(rgdSamples)/len(rgdSamples) # average
    return dc

def voltmeter():
    """ Simple voltmeter. Prints measured voltage values.

    """
    # initialize
    ver = get_version()
    print ("Digilent version " + ver)
    open()
    setup_acquisition()

    # loop until CTRL-C
    try:
        while True:
            # read value
            dc = meas_vdc(0)
            print ("DC: "+ str(round(dc,4))+"V")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("End of measurement")

    # close the device
    close()

# if run stand-alone, run the voltmeter function
if __name__ == "__main__":
    voltmeter()
