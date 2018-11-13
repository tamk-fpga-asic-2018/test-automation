"""
   Based on DWF Python Example by Digilent, Inc.

"""

# from ctypes import *
from dwfconstants import *
import time
import sys
class VoltMeter:
    def __init__(self):
        try:
            if sys.platform.startswith("win"):
                self.dwf = cdll.dwf
            elif sys.platform.startswith("darwin"):
                self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
            else:
                self.dwf = cdll.LoadLibrary("libdwf.so")
        except:
            print ("Can't load DWF library. Digilent not usable.")
        
        self.n_of_samples = 4000
        self.freq = 10000000.0
        
        #declare ctype variables
        self.hdwf = c_int()
        self.sts = c_byte()
        self.IsEnabled = c_bool()
        self.rgdSamples = (c_double*self.n_of_samples)()
    
    def get_version(self):
        """ Returns DWF version as string
    
        """
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)
        return str(version.value.decode("utf-8"))
    
    def open(self):
        """ Open the device
    
        """
        print ("Opening first device")
        self.dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
    
        if self.hdwf.value == hdwfNone.value:
            raise IOError("failed to open Analog Discovery 2 device")
    
    def close(self):
        if self.hdwf is None:
            self.dwf.FDwfDeviceCloseAll()
        else:
            self.dwf.FDwfDeviceClose(self.hdwf)
    
            
    #set up acquisition
    def setup_acquisition(self):
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(self.freq))
        self.dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(self.n_of_samples))
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(0), c_bool(True))
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(0), c_double(5))
        self.dwf.FDwfAnalogInChannelOffsetSet(self.hdwf, c_int(0), c_double(2.5))
        # pvoltsrange=c_double()
        # self.dwf.FDwfAnalogInChannelRangeGet(self.hdwf, c_int(0), byref(pvoltsrange))
        # print(pvoltsrange)
    
        # wait at least 2 seconds for the offset to stabilize
        time.sleep(2)
    
    
    def meas_vdc(self, channel=0):
        # begin acquisition
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_bool(False), c_bool(True))
        # print ("   waiting to finish")
    
        while True:
            self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(1), byref(self.sts))
            # print ("STS VAL: " + str(self.sts.value) + "STS DONE: " + str(DwfStateDone.value))
            if self.sts.value == DwfStateDone.value :
                break
            time.sleep(0.1)
        # print ("Acquisition finished")
    
        self.dwf.FDwfAnalogInStatusData(self.hdwf, channel, self.rgdSamples, self.n_of_samples) # get data
    
        dc = sum(self.rgdSamples)/len(self.rgdSamples) # average
        return dc

def run_voltmeter():
    """ Simple voltmeter. Prints measured voltage values.

    """
    # initialize
    ver = vm.get_version()
    print ("Digilent version " + ver)
    vm.open()
    vm.setup_acquisition()

    # loop until CTRL-C
    try:
        while True:
            # read value
            dc = vm.meas_vdc(0)
            print ("DC: "+ str(round(dc,4))+"V")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("End of measurement")

    # close the device
    vm.close()

# if run stand-alone, run the voltmeter function
if __name__ == "__main__":
    vm = VoltMeter()
    run_voltmeter()
