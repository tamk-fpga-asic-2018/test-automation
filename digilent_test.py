import framework


voltmeter = framework.VoltMeter()
voltmeter.open()
voltmeter.setup_acquisition()

print(voltmeter.read())