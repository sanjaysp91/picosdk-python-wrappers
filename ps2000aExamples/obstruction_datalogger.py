import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import time

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open PicoScope 2000 Series device
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])


enabled = 1
disabled = 0
analogue_offset = 0.0
channel_range = ps.PS2000A_RANGE['PS2000A_10V']

# Set up channel A
status["setChA"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChA"])

# Set up channel B
status["setChB"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_B'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChB"])

# Set up channel C
status["setChC"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_C'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChC"])

# Set up channel D
status["setChD"] = ps.ps2000aSetChannel(chandle,
                                        ps.PS2000A_CHANNEL['PS2000A_CHANNEL_D'],
                                        enabled,
                                        ps.PS2000A_COUPLING['PS2000A_DC'],
                                        channel_range,
                                        analogue_offset)
assert_pico_ok(status["setChD"])

# Size of capture
sizeOfOneBuffer = 500
numBuffersToCapture = 1000
sampleInterval = ctypes.c_int32(20)
sampleUnits = ps.PS2000A_TIME_UNITS['PS2000A_NS']
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
status["setDataBuffersB"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_B'],
                                                     bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersB"])

# Set data buffer location for data collection from channel C
status["setDataBuffersC"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_C'],
                                                     bufferCMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersC"])

# Set data buffer location for data collection from channel D
status["setDataBuffersD"] = ps.ps2000aSetDataBuffers(chandle,
                                                     ps.PS2000A_CHANNEL['PS2000A_CHANNEL_D'],
                                                     bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     sizeOfOneBuffer,
                                                     memory_segment,
                                                     ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersD"])


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
actualSampleIntervalNs = actualSampleInterval * 1000

print("Capturing at sample interval %s ns" % actualSampleIntervalNs)

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
    if autoStop:
        autoStopOuter = True


# Convert the python function into a C function pointer.
cFuncPtr = ps.StreamingReadyType(streaming_callback)

# Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
while nextSample < totalSamples and not autoStopOuter:
    wasCalledBack = False
    status["getStreamingLastestValues"] = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
    if not wasCalledBack:
        # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
        # again.
        time.sleep(0.01)

print("Done grabbing values.")

# Find maximum ADC count value
# handle = chandle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])

# Convert ADC counts data to mV
adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)
adc2mVChBMax = adc2mV(bufferCompleteB, channel_range, maxADC)
adc2mVChCMax = adc2mV(bufferCompleteC, channel_range, maxADC)
adc2mVChDMax = adc2mV(bufferCompleteD, channel_range, maxADC)

# Create time data
time = np.linspace(0, (totalSamples-1) * actualSampleIntervalNs, totalSamples)

# Plot data from channels A-D
plt.plot(time/1e9, adc2mVChAMax[:])
plt.plot(time/1e9, adc2mVChBMax[:])
plt.plot(time/1e9, adc2mVChCMax[:])
plt.plot(time/1e9, adc2mVChDMax[:])
plt.xlabel('Time (s)')
plt.ylabel('Voltage (mV)')
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
