
### INTRODUCTION ###

# Some acronyms before we get started:
#   pb2     Protobuf
#   ZMQ     ZeroMQ, 0MQ, etc. Asynchronous messaging library, networking related
#   CIL     CIRN Interaction Language (see SC2 competition, and [https://github.com/SpectrumCollaborationChallenge/CIL])
#   gpsd    GPS (data ?), as in global position system


## IMPORTS ##
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


## dragonradio LIBRARY ##
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

## dragon MODULE ##
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


# ================================================== #
### BACKGROUND ###
## asyncio ##
import asyncio

# Asyncio is used for concurrent programming (functions aka routines running in parallel), 
# and it is particularly well-suited for networking like we need with dragonradio. 

# Here's a simple hello world script from the docs 
async def main():
    print('Hello ...')
    await asyncio.sleep(1)
    print('...World!')
loop = asyncio.get_event_loop()
loop.create_task(main()) # Option 1: Create tasks, run forever
loop.run_forever()
# Hello ...
# [after 1s]
# ... World!
# [endless loop]

# Now the loop task stack is empty

loop.run_until_complete(main())) # Option 2: Run until new task is complete
# Hello ...
# [after 1s]
# ... World!
# [finished]

# Now the loop task stack is empty again

# NOTE You'll see this fairly often in tutorial online:
#asyncoi.run(main()) # Python3.7+ only (we use 3.5)
# This doesn't apply to our version of python/aynscio.

# A quite point about run_until_compelete(). You must supply a 
# coroutine to it, which is then wrapped as a task automatically.
# Then every task is run like normal, including the new task, 
# and we stop when the new task is finished. 
# For example:
loop.create_task(main())
loop.run_until_complete(main())
# Hello ...
# Hello ...
# ... World!
# ... World!
# [finished]

# We see here that both main() tasks are run. So we don't 
# need to use create_task if we only have one task. 

# So how does this all work? 

# Asyncio is a concurrency platform which allows asynchronous programming. It
# runs in a single thread, but allows asynchronous behavior.

# Terminology:
#   Concurrency - Instructions are interleaved, but only one 
#       is executing at a time (round-robin style)
#   Parallelism - Actual parallel execution of instructions
#   Asynchronous - The concept of starting a task and then
#       performing other tasks while waiting for the first to
#       finish up or continue
#   Blocking call - An instruction that must wait for e.g. a 
#       response from the network, or for a timer to finish,
#       so execution is 'blocked'

# Parts of asyncio:
#   Event Loop - Runs tasks one after another
#   Coroutine - Co-operative routine, like a function but
#       instead of returning and going out of scope it sort of
#       'pauses' its execution, keeping its state until it resumes.
#       The coroutine should pause whenever it is running a blocking call.       
#   Task - A wrapper around a coroutine which is actually kept by the event loop

# So returning to the example, things should make a little more sense.
async def testco():   # Define a coroutine with async
    print("Foo bar ...") # First executed
    await asyncio.sleep(1)  # Release control, telling the event loop what you're waiting on
    print("... Baz Qux!") # After control is returned

# Create an event loop object we can use
loop = asyncio.get_event_loop()
# Manually create a task to be run
loop.create_task(testco)
# Run this thing
loop.run_forever()

# This example is not particularly useful. We don't get much understanding of async,
# await, and how to manage our event loop. Let's take these in turn.

# async KEYWORD #
# async is a keyword (as of Python 3.5) which is typically used to define a coroutine.
# You will also see 'async with' and 'async for'. It's worth noting that async does
# NOT make the coroutine concurrent all on its own. It provides the interface so that 
# the coroutine can be used concurrently. 

# Now consider the scenario where you need to use a file like this:
with open('myfile.txt') as f:
    # Do something with f
# No more f
# If we're in a coroutine, and we want to do something like this where instead of open
# we have another coroutine, we need to use 'async with' instead of the plain 'with'.
    # ... inside a coroutine
    async with some_async_fun(file) as f:
        #...
    #...
# A similar problem arises with list comprehensions, like 
matrix = [i for i in otherarray]
# If the comprehension uses an asynchronous function, we need to use async for.
    # ... inside a coroutine
    g = [i async for i in some_async_fun()]

# await KEYWORD #
# When we have a coroutine, and we want to make a blocking call by e.g. listening for 
# incoming packets (say with listen_packets()), we know the call will hold things up. 
# So we want to release control. We do that by putting 'await' before the blocking
# call. Then control is released back to the event loop while our call is in progress.

# Ex. If listen_packets() is a function that waits for the next incoming packet, which
# can take several seconds 
async def packet_catcher():
    # [opt] do stuff
    packets = await listen_packets()
    # [opt] do other stuff

# Now when packet_catcher is added asa task to the event loop, it runs until it gets to
# listen_packets(). Control is returned to the event loop, until listen_packets() 
# returns. Then the event loop will return control to packet_catcher() when it has
# an opportunity. 

# For the await keyword to work, the function must be 'awaitable'. This means it must
# be a coroutine, a task, or a future. A future is a low-level object representing
# the eventual result of an asynchronous operation (cite: from the Python docs).

# Evidently from our first example, asyncio provides timeout coroutines like
# asyncio.wait_for(coroutine,timeout)   => On timeout throws the error asyncio.TimeoutError
# asyncio.sleep(time)   => Wait for 'time' seconds

# RUNNING SEQUENCES #
# We have the option to always make a loop object, then create successive tasks, then
# run the loop forever (or until completed). However, this is not ideal in many cases.
# For example, if you want to await with multiple coroutines, like listening on multiple
# ports. For this we can use asyncio.gather()
async def example():
    await asyncio.gather(coroutine1(),coroutine2(),coroutine3())
# Much better.
# =================================== #






