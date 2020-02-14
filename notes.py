# RADIO ARCHITECTURE
#
# Expecting something like this:
# Format: Stage (Output)
# 
# Front-end (IQ data) -> Channelizer (IQ data) -> PHY (Radio Packets) -> NET (network packets)
#
# Packet path from channelizer to tun/tap is:
#  channelizer -> controller -> PacketCompressor.radio -> FlowPerformance.radio -> tun/tap
# Packet path from tun/tap to synthesizer is:
#  tun/tap -> NetFilter -> FlowPerformance.net -> NetFirewall -> PacketCompressor.net -> NetQueue -> controller -> synthesizer


# READING LOG FILES
# The logs are written to HDF5 files (.h5) which are hierarchical data storage files.
# At each point in the file, we have either a dataset (which can be any data), or 
# a group of datasets and other groups. 
#
# Here, we have the following groups:
#   event       | Timestamp + string (e.g. for event, it could be some timestamp + ACK)
#   recv        | 
#   send        | 
#   selftx 
#   slots
#   snapshots
# We can see this with the following. 

import h5py
f = h5py.File('radio.h5','r') # Open file
list(f.keys())  # See what the keys are
# ['event','recv','selftx','send','slots','snapshots']
# Let's look at 'event'
eventset = f['event']
eventset
# <HDF5 dataset "event": shape (119,),type "|V16">
eventset.value
# array([( 0.89823448, b'SYSTEM: ifconfig tap0 > /dev/null 2>&1 (256)'),
#        ( 0.90142638, b'SYSTEM: ip tuntap add dev tap0 mode tap user root (0)'),
#       etc

# The 'recv' dataset is:
# array([(66.15147331,   -940,  22168, 1, 1, 2, 1,   0, 2, 1, 6, 27, 1, 40, -19.531538, -25.466951, 0.00831892, 0., 1000000., 0.05090981, 1518, array([ 0.62538874-0.6553724j , -0.69103426-0.56926966j,
#        -0.614056  +0.65157735j, ...,  0.7070603 +0.7176631j ,
#        -0.86840314+0.6317875j ,  0.6448208 +0.62990636j], dtype=complex64)),
#        ...
# These all have a format:
# dtype={'names':
#   ['timestamp','start_samples','end_samples','header_valid','payload_valid',
#   'curhop','nexthop','seq','src','dest','crc','fec0','fec1','ms','evm','rssi',
#   'cfo','fc','bw','demod_latency','size','iq_data'], 'formats':['<f8','<i4',
#   '<i4','u1','u1','u1','u1','<u2','u1','u1','<i4','<i4','<i4','<i4','<f4','<f4',
#   '<f4','<f4','<f4','<f4','<u4','O'], 'offsets':[0,8,12,16,17,18,19,20,22,23,24,
#   28,32,36,40,44,48,52,56,60,64,72], 'itemsize':88}) 

# dtype={'names':['timestamp','curhop','nexthop','seq','src','dest','crc','fec0',
#   'fec1','ms','fc','bw','size','iq_data'], 'formats':['<f8','u1','u1','<u2','u1',
#   'u1','<i4','<i4','<i4','<i4','<f4','<f4','<u4','O'], 'offsets':[0,8,9,10,12,13,
#   16,20,24,28,32,36,40,48]

# 

