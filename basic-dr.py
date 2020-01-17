# Some acronyms before we get started:
#   pb2     Protobuf
#   ZMQ     ZeroMQ, 0MQ, etc. Asynchronous messaging library, networking related
#   CIL     CIRN Interaction Language (see SC2 competition, and [https://github.com/SpectrumCollaborationChallenge/CIL])
#   gpsd    GPS (data ?), as in global position system


# IMPORTS
import argparse # Argument parsing from command line 
import asyncio  # Event-driven framework
from concurrent.futures import CancelledError   # Just an error 
import IPython  # Interactive Python (IPython, now Jupyter)
from itertools import chain, cycle, starmap # ?
import logging  # ?
import os       # Operating system utilities
import random   # Random number generator
import signal   # ?
import sys      # System utilities (e.g. running commands on the command line)

import dragonradio  # Dragonradio library python bindings 
import dragon.radio # Dragon module Radio class, utility class 


# dragonradio LIBRARY
# The dragonradio bindings expose the following:
#   LiquidEnums
#   Clock
#   Logger
#   RadioConfig   
#   WorkQueue
#   USRP
#   MCS
#   Estimators
#   Net
#   CIL
#   Flow
#   RadioNet
#   PHYs
#   Channels
#   Channelizers
#   Synthesizers
#   Controllers
#   MACs
#   Resamplers
#   NCOs (Numerically Controlled Oscillators)
#   Filters
#   IQBuffer
#   IQCompression
#   Snapshot
# The module itself is called dragonradio. To import one of the above, simply
# use e.g. 
# from dragonradio import Estimators 

# Of interest here is IQBuffer, which is defined in the following way
from dragonradio import IQBuffer
# IQBuf     Class
#   init()
#   init(std::complex<float>*)      32 bit complex float
#   timestamp       Buffer time stamp in seconds
#   fc              Center frequency
#   fs              Sample frequency
#   delay           Signal delay
#   data            IQ data

# dragon MODULE
# Within the dragon module we have the following:
#   dragon.channels         Channel plans (only one default method)
#   dragon.collab           Something to do with sc2 contest?
#   dragon.controller       Manages nodes for contest? More?
#   dragon.gpsd             GPS data
#   dragon.internal_pb2     Internal with protobuf (pb2)
#   dragon.internal         More competition stuff? 
#   dragon.protobuf         Serialization (turning program data into binary)
#   dragon.radio            Main radio module
#   dragon.remote_pb2       Remote with protobuf (pb2)
#   dragon.remote           Remote interface for contest?
#   dragon.schedule         TDMA scheduling
#   dragon.signal           Some signal processing utilities


# The most important of these is dragon.radio, the main radio class and
# supporting methods and classes. It uses these dragonradio library 
# modules:
from dragonradio import Channel, Channels, MCS, TXParams, TXParamsVector

# The following are top-level methods:
#   fail(msg)       Prints an error message
#   getNodeIdFromHostname()     Find the node id for this host
#   safeRate(min_rate, clock_rate)      Find a safe rate no less than min_rate
#       given the clock rate clock_rate

# Then we get the following classes:
#   ExtendAction
#   LogLevelAction
#   LoadConfigAction
#   Config
#   Radio

# The most important classes are Config and Radio

# Config is a simple data structure class for all the radio parameters,
# so note that it does not interact with the DragonRadio library. It just 
# stores values for everything in the radio, and allows us to specify those
# values with hard-coded defaults and by supplying arguments on the command
# line. A Config object is used ONLY TO INITIALIZE THE RADIO OBJECT

# Radio is the top level radio class. It is constructed using a Config object,
# which is stored as self.config

# The Radio init() function (the constructor) performs the following upon
# initialization:
#   Set config
#   Set node ID
#   Initialize logger (defaults to None)   
#   Set lock for asyncio
#   Set logger info
#   Copy configuration settings to C++ RadioConfig object
#   Add global work queue workers
#   Set default TX channel index
#   Create USRP object (dragonradio.USRP class)
#   Set TX and RX rates to None so they are properly set by setTXRate and setRXRate
#   Create logger after USRP so there is a global clock
#   Configure snapshots
#   Configure PHY
#   Configure MAC
#   Configure tun/tap interface and net neighborhood
#   Configure channelization
#   Configure controller (empty)
#   Create TX parameters
#   Create flow performance measurement component
#   Create packet compression component
#   Configure packet path from channelizer to tun/tap
#   Configure packet path from tun/tap to synthesizer
#   Tell SmartController about network queue, if using it
#   Configure channels

# As well, the following class methods are defined:
#   configTXParamsSoftGain(tx_params)
#   setTXParams(crc,fec0,fec1,ms,g,clip=0.999)
#   configureDefaultChannels()   
#   setChannels(channels)
#   setRXRate(rate)
#   setTXRate(rate)
#   setSynthesizerTXChannel(channel)
#   setTXChannel(channel_idx)
#   reconfigureBandwidthAndFrequency(bandwidth,frequency)
#   genChannelizerTaps(channel)
#   genSynthesizerTaps(channel)
#   deleteMAC()
#   configureALOHA()
#   configureTDMA(nslots)
#   finishConfiguringMAC()
#   setALOHAChanell(channel_idx)
#   installALOHASchedule()
#   installMACSchedule(sched)
#   configureSimpleMACSchedule()
#   SynchronizeClock()
#   timetampRegression(echoed,master)   Perform linear regression of timestamps to determine clockskew and delta
#   NOTE: Should be timestampRegression()?
#   timetampRegressionNoSkew(echoed,master)
#   getRadioLogPath()
#   snapshotLogger()    ( Asynchronous )




