import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
import os

folder = "20240624_222541"
filename = "picoscope_data_allInOne"
filename = os.path.join(folder, filename)

# Load the .mat file
data = loadmat(filename) 

# Extract the data arrays
bufferA = data['bufferA']
bufferB = data['bufferB']
bufferC = data['bufferC']
bufferD = data['bufferD']

# Assuming bufferA, bufferB, bufferC, bufferD are 1D arrays of the same length

# Plotting the data
time = np.linspace(0, len(bufferA) - 1, len(bufferA))  # Create a time array

plt.figure(figsize=(10, 6))

plt.subplot(4, 1, 1)
plt.plot(time, bufferA, label='Channel A')
plt.xlabel('Time')
plt.ylabel('Voltage (Channel A)')
plt.legend()

plt.subplot(4, 1, 2)
plt.plot(time, bufferB, label='Channel B')
plt.xlabel('Time')
plt.ylabel('Voltage (Channel B)')
plt.legend()

plt.subplot(4, 1, 3)
plt.plot(time, bufferC, label='Channel C')
plt.xlabel('Time')
plt.ylabel('Voltage (Channel C)')
plt.legend()

plt.subplot(4, 1, 4)
plt.plot(time, bufferD, label='Channel D')
plt.xlabel('Time')
plt.ylabel('Voltage (Channel D)')
plt.legend()

plt.tight_layout()
plt.show()
