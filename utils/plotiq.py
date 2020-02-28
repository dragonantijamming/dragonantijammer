# Plot data in iqdatatest.dat
# (Comma-separated complex data)

import csv
import cmath
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import signal
from scipy import fftpack

# Open IQ data, store as Cdata (complex data)
iqdata_all = []
with open('iqdatatest.dat','r') as csvfile:
    datareader = csv.reader(csvfile,delimiter=',')
    Idata = []
    Qdata = []
    for row in datareader:
        Idata.append(float(row[0]))
        Qdata.append(float(row[1]))
Cdata = Idata + np.multiply(Qdata,1j)
# Now we have Idata and Qdata as lists of float data, as well as full complex data

# Take FFT of IQ data
N = len(Idata)
X_k = fftpack.fft(Cdata)/N # Note: 1/N scaling factor
#X_k = fftpack.fftshift(Cdata)

# Now need to shift the FFT to get only the upper half of the spectrum
kstart = 1
kend = 1
if N%2 == 0:
    kend = int(N/2)
else:
    kend = int((N-1)/2)
X_k = np.concatenate( (X_k[kend:],X_k[0:kend]) ) # TODO Squash dimension down or use stack

# Plot fft in dB vs omega (w)
w = np.arange(N)
X_db = 20*np.log10(np.abs(X_k)) 

print("Signal energy: "+str(np.abs(np.trapz(X_k)))) # Print signal energy

plt.plot(w,np.abs(X_k),'k') 
plt.show()


