
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

from Morelia.Devices import Pod8206HR
from Morelia.Devices import Pod8206HRTest
from Morelia.packet.data import DataPacket
from Morelia.Stream.sink import InfluxSink, EDFSink, CSVSink
import Morelia.Stream.data_flow as data_flow
import time
import pyedflib
import matplotlib.pyplot as plt
import numpy as np

MAX_DAC_VALUE = 65535

def get_ttl_states(pod) -> list[int]:
    response = pod.WriteRead('GET TTL PORT')
    payload_str = response.raw_packet[1:-1] #takes off STX and ETX
    hex_payload = payload_str[4:6].decode('ascii') #gets payload and turns b'50' into 50
    payload_int = int(hex_payload, 16) #turns hex 50 into int 80
    binary_str = format(payload_int, '08b') #turns int 80 into binary 01010000
    # print(binary_str[:4])
    return [binary_str[:4]]

def get_frequency(pod) -> list[int]:
    for x in range(5):
        pod.WriteRead('GET FREQ')
    response = pod.WriteRead('GET FREQ')
    payload_str = response.raw_packet[1:-1] #takes off STX and ETX
    # print(payload_str)
    hex_payload = payload_str[4:8].decode('ascii') #gets payload and turns b'0028' into 0028
    payload_int = int(hex_payload, 16) #turns hex 0028 into int 40
    print("Frequency: " + str(payload_int))
    return payload_int

def get_amplitude(pod) -> list[int]:
    for x in range(5):
        pod.WriteRead('GET AMP')
    response = pod.WriteRead('GET AMP')
    payload_str = response.raw_packet[1:-1] #takes off STX and ETX
    # print(payload_str)
    hex_payload = payload_str[4:8].decode('ascii') #gets payload and turns b'0028' into 0028
    payload_int = int(hex_payload, 16) #turns hex 0028 into int 40
    print("Amplitude: " + str(payload_int))
    return payload_int

#this function doesn't work just yet because of the race condition, but it will work once that is fixed
def get_digital_state(podTest, pin) -> list[int]:
    # podTest.WriteRead('GET DIGITAL IO', (pin)) # first time this is called it gets a set command packet for some reason (race condition)
    # podTest.WriteRead('GET DIGITAL IO', (pin))
    responseTest = podTest.WriteRead('GET DIGITAL IO', (pin))
    payload_str = responseTest.raw_packet[1:-1] #takes off STX and ETX
    # print(payload_str)
    hex_payload = payload_str[4:6].decode('ascii') #gets payload and turns b'50' into 50
    # print(hex_payload)
    payload_int = int(hex_payload, 16) #turns hex 50 into int 80
    # print(payload_int)
    return payload_int

def plotEDF(edfFile, channel, startTime, endTime, title):
     # 1) Open the EDF
     f = pyedflib.EdfReader(edfFile)
     # 2) List channel names
     ch_names = f.getSignalLabels()
     # 3) Read the channel 0
     sig = f.readSignal(channel)
     fs = f.getSampleFrequency(channel)
     t = np.arange(len(sig)) / fs

     # Create subplots
     plt.subplots(figsize=(10, 6))
     # Plot the channel
     plt.plot(t, sig)
     plt.xlabel("Time (s)")
     plt.ylabel(ch_names[channel])
     plt.title(title)
     plt.xlim(startTime, endTime)
    #  min_val = min([min(signal) for signal in sig])
    #  max_val = max([max(signal) for signal in sig])
    #  margin = (max_val - min_val) * 0.1 # Add a 10% margin
    #  plt.ylim(min_val - margin, max_val + margin)
     # Show plot
     plt.show()
     print(np.average(np.abs(sig)))
     print(np.max(sig))
     
     f.close()


# Connect to an 8206HR devices on on /dev/ttyUSB0-2 and set the preamplifer gain to 10.
pod = Pod8206HR('/dev/ttyUSB0', 10)
# print("sample_rate is:", pod.sample_rate, type(pod.sample_rate))
if isinstance(pod.sample_rate, tuple):
    pod.sample_rate = pod.sample_rate[0]


# Clear contents from file
with open("testFile.txt", "w") as file:
    for x in range(50):
        file.write("~")
    file.write("\n\n")
# Connect to an 8206HRTest device on /dev/ttyUSB1
podTest = Pod8206HRTest('/dev/ttyUSB1')
# print("sample_rate is:", podTest.sample_rate, type(podTest.sample_rate))
if isinstance(podTest.sample_rate, tuple):
    podTest.sample_rate = podTest.sample_rate[0]

# # This doesn't work right now because of the race condition, but it will once that is fixed
# podTest.WritePacket('SET DIGITAL IO', (1, 0))
# podTest.WritePacket('SET DIGITAL IO', (2, 1))
# podTest.WritePacket('SET DIGITAL IO', (3, 0))
# podTest.WritePacket('SET DIGITAL IO', (4, 1))
# with open("testFile.txt", "a") as file:
#     file.write("Setting TTL[1-4] to [0101] on Tester.\n")
#     file.write("Set TTL1 to LOW: " + str(get_digital_state(podTest, 1)) + "\n")
#     file.write("Set TTL2 to HIGH: " + str(get_digital_state(podTest, 2)) + "\n")
#     file.write("Set TTL3 to LOW: " + str(get_digital_state(podTest, 3)) + "\n")
#     file.write("Set TTL4 to HIGH: " + str(get_digital_state(podTest, 4)) + "\n")

#     file.write("\nRead the TTL pins on 8206HR.\n")
#     file.write(str(get_ttl_states(pod)) + "\n")

# pod.WritePacket('SET TTL OUT', (0, 1) )
# pod.WritePacket('SET TTL OUT', (1, 0) )
# pod.WritePacket('SET TTL OUT', (2, 1) )
# pod.WritePacket('SET TTL OUT', (3, 0) )
# with open("testFile.txt", "a") as file:
#      file.write("\nSetting TTL[1-4] to [1010] on 8206HR.\n")
#      file.write("\nRead the TTL pins on Tester.\n")
#      file.write("TTL1: " + str(get_digital_state(podTest, 1)) + "\n")
#      file.write("TTL2: " + str(get_digital_state(podTest, 2)) + "\n")
#      file.write("TTL3: " + str(get_digital_state(podTest, 3)) + "\n")
#      file.write("TTL4: " + str(get_digital_state(podTest, 4)) + "\n")








podTest.WritePacket('SET CHANNEL', 1) # Sets channel to DAC A
podTest.WritePacket('SET FREQ', 40)
podTest.WritePacket('SET AMP', int(MAX_DAC_VALUE / 5))
# print(get_amplitude(podTest))
podTest.WritePacket('SET SINE WAVE')

# Create EDF sinks.
edf_dump = EDFSink('dump_1.edf', podTest)
edf_dump2 = EDFSink('dump_2.edf', pod)
# List that defines how sources map to sinks.
mapping = [(podTest, [edf_dump]),
           (pod, [edf_dump2])]
flowgraph = data_flow.DataFlow(mapping)

# Start data collection in background
flowgraph.collect_for_seconds(5)
# flowgraph.collect()
# time.sleep(5)

f = pyedflib.EdfReader("dump_1.edf")
with open("testFile.txt", "a") as file:
    # file.write("\nSet Sine wave with freq " + str(get_frequency(podTest)) + " and amp " + str(get_amplitude(podTest)) + "\n")
    file.write("Channel 1\n")
    file.write(str(np.average(abs(f.readSignal(0)))))
    samples = f.readSignal(0)
    file.write("\nMin: " + str(min(samples)) + " Max: " + str(max(samples)) + "\n")
    # file.write("Sample rate of first sine wave: " + str(f.getSampleFrequency(0)) + "\n")
f.close()

plotEDF("dump_1.edf", 0, 0, 21, "DAC_A")


podTest.WritePacket('SET CHANNEL', 2)
# podTest.WritePacket('SET SINE WAVE')
# podTest.WritePacket('SET FREQ', 60)
podTest.WritePacket('SET AMP', int(MAX_DAC_VALUE / 50))
# Create EDF sinks.
edf_dump = EDFSink('dump_1.edf', podTest)
edf_dump2 = EDFSink('dump_2.edf', pod)
# List that defines how sources map to sinks.
mapping = [(podTest, [edf_dump]),
           (pod, [edf_dump2])]
flowgraph = data_flow.DataFlow(mapping)

flowgraph.collect_for_seconds(5)
# flowgraph.collect()
# time.sleep(5)
# flowgraph.stop_collection()

f = pyedflib.EdfReader("dump_1.edf")
fHR = pyedflib.EdfReader("dump_2.edf")
with open("testFile.txt", "a") as file:
    # file.write("\nSet Sine wave with freq " + str(get_frequency(podTest)) + " and amp " + str(get_amplitude(podTest)) + "\n")
    file.write("Channel 2\n")
    file.write(str(np.average(abs(f.readSignal(1)))))
    samples = f.readSignal(1)
    file.write("\nMin: " + str(min(samples)) + " Max: " + str(max(samples)) + "\n")
    file.write("\nEEG2 to see if it's the same\n")
    samples = fHR.readSignal(1)
    file.write(str(np.average(abs(fHR.readSignal(1)))))
f.close()
fHR.close()

plotEDF("dump_1.edf", 1, 0, 11, "DAC_B")
plotEDF("dump_2.edf", 1, 0, 11, "EEG2")

# # 1) Open the EDF
# f = pyedflib.EdfReader("dump_1.edf")

# # 2) List channel names
# ch_names = f.getSignalLabels()
# print("Channels:", ch_names)

# # 3) Read the channel 0
# sig_0 = f.readSignal(0)
# fs_0 = f.getSampleFrequency(0)
# t_0 = np.arange(len(sig_0)) / fs_0

# # Read the channel 1
# sig_1 = f.readSignal(1)
# fs_1  = f.getSampleFrequency(1)
# t_1 = np.arange(len(sig_1)) / fs_1

# # Read channel 2
# sig_2 = f.readSignal(2)
# fs_2  = f.getSampleFrequency(2)
# t_2 = np.arange(len(sig_2)) / fs_2

# # Create subplots
# fig, axs = plt.subplots(1, 3, figsize=(10, 6))  # 1 rows, 3 columns

# # 1) Plot a channel 0
# axs[0].plot(t_0, sig_0)
# axs[0].set_xlabel("Time (s)")
# axs[0].set_ylabel(ch_names[0])
# axs[0].set_title("DAC_A")
# axs[0].set_xlim(0, 0.1)  # first 5 seconds

# # Plot channel 1
# axs[1].plot(t_1, sig_1)
# axs[1].set_xlabel("Time (s)")
# axs[1].set_ylabel(ch_names[1])
# axs[1].set_title("DAC_B")
# axs[1].set_xlim(0, 0.1)  # first 5 seconds

# # Plot channel 2
# axs[2].plot(t_2, sig_2)
# axs[2].set_xlabel("Time (s)")
# axs[2].set_ylabel(ch_names[2])
# axs[2].set_title("DAC_C")
# axs[2].set_xlim(0, 0.1)  # first 5 seconds


# # Adjust layout
# plt.tight_layout()
# plt.show()


