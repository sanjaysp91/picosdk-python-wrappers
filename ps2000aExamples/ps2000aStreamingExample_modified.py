# PS2000 Series (A API) STREAMING MODE EXAMPLE
# This example demonstrates how to call the ps2000a driver API functions in order to open a device, setup 4 channels and collects streamed data (1 buffer).
# This data is then plotted as adc counts against time in us.

import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import time
from scipy.io import savemat
import os
from datetime import datetime

# Create a directory named with the current timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs(timestamp, exist_ok=True)
# code control 
flag_measExecTimeDur = True # flag to enable execution time duration measurement 
# flag_saveAsMatFile_each = True
flag_saveAsMatFile_combined = True 
flag_plotData = False 
# if flag_saveAsMatFile_each:
#     global readout_counter
# functions to time execution 
def tic():
    global start_time
    start_time = time.perf_counter()
def toc():
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    return elapsed_time

# function to save data in MAT format:
def save_to_mat(folder, filename, time_s, bufferA, bufferB, bufferC, bufferD):
    data_dict = {
        'time_s': time_s,
        'bufferA': bufferA,
        'bufferB': bufferB,
        'bufferC': bufferC,
        'bufferD': bufferD
    }
    filename = os.path.join(folder, filename)
    savemat(filename, data_dict)
    print(f"Data saved to {filename}")

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open PicoScope 2000 Series device
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])
print("debug: status of openunit:", status["openunit"], "handle value:", chandle.value)

enabled = 1
disabled = 0
analogue_offset = 0.0

# Set up channel A
# handle = chandle
# channel = PS2000A_CHANNEL_A = 0
# enabled = 1
# coupling type = PS2000A_DC = 1
# range = PS2000A_10V = 9
# analogue offset = 0 V
channel_range = ps.PS2000A_RANGE['PS2000A_10V']
status["setChA"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChA"])

# Set up channel B
# handle = chandle
# channel = PS2000A_CHANNEL_B = 1
# enabled = 1
# coupling type = PS2000A_DC = 1
# range = PS2000A_10V = 9
# analogue offset = 0 V
status["setChB"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_B'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChB"])

# Set up channel C
# handle = chandle
# channel = PS2000A_CHANNEL_C = 2
# enabled = 1
# coupling type = PS2000A_DC = 1
# range = PS2000A_5V = 8
# analogue offset = 0 V
status["setChC"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_C'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChC"])

# Set up channel D
# handle = chandle
# channel = PS2000A_CHANNEL_D = 3
# enabled = 1
# coupling type = PS2000A_DC = 1
# range = PS2000A_500MV = 5
# analogue offset = 0 V
status["setChD"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_D'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChD"])

# Size of capture
sizeOfOneBuffer =int(1e6) # 1s data [#1ms:1e3 #1s:1e6] 
numBuffersToCapture = int(1e1) # 10 buffers 
totalSamples = sizeOfOneBuffer * numBuffersToCapture

# Create buffers ready for assigning pointers for data collection
bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
bufferCMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
bufferDMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)

memory_segment = 0

# Set data buffer location for data collection from channel A
# handle = chandle
# source = PS2000A_CHANNEL_A = 0
# pointer to buffer max = ctypes.byref(bufferAMax)
# pointer to buffer min = ctypes.byref(bufferAMin)
# buffer length = maxSamples
# segment index = 0
# ratio mode = PS2000A_RATIO_MODE_NONE = 0
status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                                                     bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersA"])

# Set data buffer location for data collection from channel B
# handle = chandle
# source = PS2000A_CHANNEL_B = 1
# pointer to buffer max = ctypes.byref(bufferBMax)
# pointer to buffer min = ctypes.byref(bufferBMin)
# buffer length = maxSamples
# segment index = 0
# ratio mode = PS2000A_RATIO_MODE_NONE = 0
status["setDataBuffersB"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_B'],
                                                     bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersB"])

# Set data buffer location for data collection from channel C
# handle = chandle
# source = PS2000A_CHANNEL_C = 2
# pointer to buffer max = ctypes.byref(bufferCMax)
# pointer to buffer min = ctypes.byref(bufferCMin)
# buffer length = maxSamples
# segment index = 0
# ratio mode = PS2000A_RATIO_MODE_NONE = 0
status["setDataBuffersC"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_C'],
                                                     bufferCMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersC"])

# Set data buffer location for data collection from channel D
# handle = chandle
# source = PS2000A_CHANNEL_D = 3
# pointer to buffer max = ctypes.byref(bufferDMax)
# pointer to buffer min = ctypes.byref(bufferDMin)
# buffer length = maxSamples
# segment index = 0
# ratio mode = PS2000A_RATIO_MODE_NONE = 0
status["setDataBuffersD"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_D'],
                                                     bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersD"])

# Begin streaming mode:
sampleInterval = ctypes.c_int32(1)
sampleUnits = ps.PS2000A_TIME_UNITS['PS2000A_US']
# We are not triggering:
maxPreTriggerSamples = 0
autoStopOn = 1
# No downsampling:
downsampleRatio = 1
status["runStreaming"] = ps.ps2000aRunStreaming(chandle,
                                                ctypes.byref(sampleInterval),
                                                sampleUnits,
                                                maxPreTriggerSamples,
                                                totalSamples,
                                                autoStopOn,
                                                downsampleRatio,
                                                ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'],
                                                sizeOfOneBuffer)
assert_pico_ok(status["runStreaming"])

actualSampleInterval = sampleInterval.value
actualSampleIntervalUs = actualSampleInterval * 1E6

print("Capturing at sample interval %s us" % actualSampleIntervalUs)

# We need a big buffer, not registered with the driver, to keep our complete capture in.
bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteC = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteD = np.zeros(shape=totalSamples, dtype=np.int16)
nextSample = 0
autoStopOuter = False
wasCalledBack = False


def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
    global nextSample, autoStopOuter, wasCalledBack
    wasCalledBack = True
    destEnd = nextSample + noOfSamples
    sourceEnd = startIndex + noOfSamples
    bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
    bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
    bufferCompleteC[nextSample:destEnd] = bufferCMax[startIndex:sourceEnd]
    bufferCompleteD[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
    nextSample += noOfSamples

    # # if flag is set, save the file 
    # if flag_saveAsMatFile_each: 
    #     readout_counter += 1
    #     filename = f"picoscope_data_{readout_counter}.mat"
    #     time_us = np.linspace(0, (sizeOfOneBuffer-1) * actualSampleIntervalUs, sizeOfOneBuffer) * 1E-6
    #     time_s = time_us * 1E-6
    #     save_to_mat(timestamp, filename, time_s, bufferAMax, bufferBMax, bufferCMax, bufferDMax)
    if autoStop:
        autoStopOuter = True

# Convert the python function into a C function pointer.
cFuncPtr = ps.StreamingReadyType(streaming_callback)
if flag_measExecTimeDur:
    # Start execution time duration timer (tic)
    tic()
print("debug: Started")

# Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
while nextSample < totalSamples and not autoStopOuter:
    wasCalledBack = False
    status["getStreamingLastestValues"] = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
    if not wasCalledBack:
        # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
        # again.
        time.sleep(1e-3) # wait for 1ms 
        # print("debug: Not Called Yet!")

if flag_measExecTimeDur:
    # Start execution time duration timer (tic)
    toc()
print("Done grabbing values.")

# Find maximum ADC count value
# handle = chandle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])
print("ADC maximumValue: ", maxADC.value)

minADC = ctypes.c_int16()
status["minimumValue"] = ps.ps2000aMinimumValue(chandle, ctypes.byref(minADC))
assert_pico_ok(status["minimumValue"])
print("ADC minimumValue: ", minADC.value)

# Convert ADC counts data to mV
# adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)
# adc2mVChBMax = adc2mV(bufferCompleteB, channel_range, maxADC)

# Create time data
time_us = np.linspace(0, (totalSamples-1) * actualSampleIntervalUs, totalSamples) * 1E-6
time_s = time_us * 1E-6
if flag_saveAsMatFile_combined: # if flag is set, save the file 
    filename = f"picoscope_data_allInOne.mat"
    save_to_mat(timestamp, filename, time_s, bufferCompleteA, bufferCompleteB, bufferCompleteC, bufferCompleteD)
# Plot data from channel A and B
if flag_plotData: 
    plt.plot(time_s, bufferCompleteA[:])
    plt.plot(time_s, bufferCompleteB[:])
    plt.plot(time_s, bufferCompleteC[:])
    plt.plot(time_s, bufferCompleteD[:])
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (adc)')
    plt.show()

# Stop the scope
# handle = chandle
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

# Disconnect the scope
# handle = chandle
status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# Display status returns
print(status)

