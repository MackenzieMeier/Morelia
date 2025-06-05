
# add directory path to code
# import Path
# Path.AddAPIpath()

# local imports
# import  HelperFunctions as hf
# from    Morelia.Devices  import Pod8206HRTest


# create instance of 8206-HR Test and 8206-HR POD devices

# portTest: str = Pod8206HRTest.ChoosePort()
# podTest = Pod8206HRTest(portTest)

# write each command:

# print('~~ BASICS for Test Device ~~')
# hf.RunCommand(podTest, 'PING') # Used to verify device is present and communicating
# hf.RunCommand(podTest, 'TYPE') # Returns the device type value.  This is a unique value for each device.  For the 8206HR it is 0x30
# hf.RunCommand(podTest, 'FIRMWARE VERSION') # Returns the device firmware version as 3 values.  So 1.0.10 would come back as 0x31, 0x30, 0x00, 0x41

# print('~~ WRITE and READ DIGITAL and TTL PINS ~~')
# print('~~ set DIGITAL 1 - 4 to HIGH')
# hf.RunCommand(podTest, 'SET DIGITAL IO', (1, 1)) # Sets the selected DIGITAL pin (1,2,3,4) to HIGH
# hf.RunCommand(podTest, 'SET DIGITAL IO', (2, 1)) # "
# hf.RunCommand(podTest, 'SET DIGITAL IO', (3, 1)) # "
# hf.RunCommand(podTest, 'SET DIGITAL IO', (4, 1)) # "
# print('~~ read DIGITAL 1 - 4 ~~')
# hf.RunCommand(podTest, 'GET DIGITAL IO', (1)) # Gets the value of DIGITAL 1
# hf.RunCommand(podTest, 'GET DIGITAL IO', (2)) # Gets the value of DIGITAL 2
# hf.RunCommand(podTest, 'GET DIGITAL IO', (3)) # Gets the value of DIGITAL 3
# # hf.RunCommand(podTest, 'GET DIGITAL IO', (4)) # Gets the value of DIGITAL 4


# print('~~ SET SINE WAVE ~~')
# print('~~ DAC A ~~')
# hf.RunCommand(podTest, 'SET CHANNEL', (1)) # Sets the Channel to DAC A
# hf.RunCommand(podTest, 'SET FREQ', (80)) # Sets the frequency to 40Hz
# hf.RunCommand(podTest, 'SET AMP', (13107)) # Sets the amplitude to Max DAC Value divided by 5
# hf.RunCommand(podTest, 'SET SINE WAVE') # Turns on the sine wave


# print('~~  ~~')


from    Morelia.Devices  import Pod8206HR
from Morelia.Stream.sink import EDFSink
from     Morelia.Stream  import data_flow

def main():
    # Connect to an 8206HR devices on on /dev/ttyUSB0-2 and set the preamplifer gain to 10.
    pod_1 = Pod8206HR('COM35', 10)
    # Create EDF sinks.
    edf_dump_1 = EDFSink('dump_1.edf', pod_1)
    # List that defines how sources map to sinks.
    mapping = [(pod_1, [edf_dump_1])]
    flowgraph = data_flow.DataFlow(mapping)
    flowgraph.collect_for_seconds(60)

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Optional but safe on Windows
    main()