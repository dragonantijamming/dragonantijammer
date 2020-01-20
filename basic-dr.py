
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
#   snapshotLogger()    ( asyncio coroutine )


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
### DRAGONRADIO ESSENTIALS ###

## A Simple Example Setup Script ##

# What is required in order to run the radio? How can we make a minimal example? 

# The radio has a large number of configuration parameters, relating to PHY, MAC, and
# network parameters. These parameters can be specified as command-line arguments. They
# are accepted and put into a Conig object (dragon.radio.Config) using the python argparse
# module [https://docs.python.org/3.5/library/argparse.html]. 

# Logging through the python logging module [https://docs.python.org/3.5/library/logging.html]
# can be initialized, and then a Radio object (dragon.radio.Radio) is initialized using 
# the Config object (see above, where this process was outlined in detail).

# The MAC is configured next, which happens through the Radio object. First the number of
# nodes is used to add network nodes to the Radio's Net object, then the specified MAC
# protocol (ALOHA or the default simple MAC) is configured. 

# Last, we run an asyncio loop, or start an IPython session. And that's all!

# Let's do this in a simple script. 
def main():
    config = dragon.radio.Config() # Config object from dragon.radio
    # Create argument parser object
    parser = argparse.ArgumentParser(description='Run dragonradio.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    config.addArguments(parser) # Add parser to Config object

    # Let's add an argument for the number of nodes
    parser.add_argument('-n', action='store', type=int, dest='num_nodes',default=2,
        help='set number of nodes in network')
    # And an argument for whether or not to use ALOHA MAC
    parser.add_argument('--aloha',action='store_true',dest='aloha',
        default=False,help='use slotted ALOHA MAC')
    # And an argument for interactive mode (IPython mode)
    parser.add_arguments('--interactive',action='store_true',dest='interactive',
        default=False,help='enter interactive shell after radio is configured')
    
    # Now we need to try and parse our arguments. We'll put this in a try/except
    # loop in case arguments are bad. The exception for this is SystemExit.
    try:
        parser.parse_args(namepsace=config)
    except SystemExit as ex:
        return ex.code
    
    # Next we're going to set up logging. First we use the logging module's basicConfig method.
    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
        level=config.loglevel)
    # This just sets up the log message formatting with the specified log level

    # Then share this with our Config object
    if config.log_directory:
        config.log_sources += ['log_recv_packets','log_sent_packets','log_events']
    # TODO I haven't really looked into how the logging is working so this part is a bit vague

    # Let's go ahead and create our Radio object. We initialize it with the Config object.
    radio = dragon.radio.Radio(config)

    # Setting up the MAC, first get the number of nodes, add them to the Radio object's Net object
    for i in range(0, config.num_nodes):
        radio.net.naddNode(i+1)
    
    # Choose either slotted ALOHA MAC or the default
    if config.aloha:
        radio.configureALOHA()
    else:
        radio.configureSimpleMACSchedule()
    
    # Finally we handle the program flow. Either IPython, or an asyncio loop
    if config.interactive:
        IPython.embed()
    else:
        loop = asyncio.get_event_loop() # Create an event loop
        if config.log_snapshots != 0:
            loop.create_task(radio.snapshotLogger()) # snapshotLogger is a coroutine
        
        for sig in [signal.SIGINT, signal.SIGTERM]: # Handle ctrl+C and ctrl+D
            loop.add_signal_handler(sig, cancel_loop) # Simply stop the loop
        
        # NOTE You can add other tasks here
        
        # Try running forever, and close the loop before we exit
        try:
            loop.run_forever()
        finally:
            loop.close()
    return 0

# We have our main() function, let's run it if we're the program entry point
if __name__=='__main__':
    main()

# This is everything, now the radio will run as expected. Clearly, most of the 'magic'
# is hidden within dragon.radio.Radio. There is only one coroutine defined in the
# Radio class, which is for snapshot logging. Nothing else uses the event loop in
# our simple radio, though you can add more tasks. The radio really starts running
# when the Radio object is constructed (see above description of the init) and the
# MAC is configured.

## Some Details of the Radio ##
# The dragon.radio object is a help object which hides away much of the configuration
# required for actually using the dragonradio library and bindings. It is very
# complete, however, making it useful in all experiments with the radio. Let's
# use it and the library itself to see what kind of control we have over the radio.

# USRP INTERFACING #
# The USRP object needs an address, and the antennas for transmit and receive need
# to be specified. We have the following arguments:
#   --addr
#   --rx-antenna
#   --tx-antenna

# We can lump frequency and bandwidth settings in here, too, as these are typically
# fixed during operation (normal radios, which we're simulating, can't frequency
# hop). 
# The center frequency, bandwidth, max bandiwdth, receive and transmit bandwidths, 
# receive and transmit oversampling, and channel bandwidth can be set. For example,
# we might set the bandwidth to 10 MHz centered at 1.3 GHz, and use 1 MHz channel
# bandwidths. 
# Arguments available are (all frequencies/bandwidths in Hz):
#   -f, --frequency
#   -b, --bandwidth
#   --max-bandwidth
#   --rx-bandwidth
#   --tx-bandwidth
#   --rx-oversample
#   --tx-oversample
#   --channel-bandwidth
# There are also gain options, including transmit and receive gains, and soft transmit
# gain. The arguments are (all gains in dB):
#   -G, --tx-gain
#   -R, --rx-gain
#   -g, --soft-tx-gain
#   --auto-soft-tx-gain
#   --auto-soft-tx-gain-clip-frac

# Since these are fixed parameters for a given communication system, we won't go into
# the methods available or the interface exposed from the library. They should be
# set as defaults in the Config object, or passed in as arguments when running. 
# ! DON'T SET THESE DYNAMICALLY !

# PHY LAYER #
# The PHY parameters include the PHY system (flexframe, newflexframe, and ofdm),
# packet size, number of channels, upsampling, modulation options, decoding options,
# channelizer parameters, and synthesizer parameters.

# Of particular interest here are the PHY, channelizer, and synthesizer parameters.
# PHY layer protocols available:
#   - Flexible framing (flexframe) [https://liquidsdr.org/doc/flexframe/]
#   - Orthogonal Frequency-Division Multiplexing (OFDM) 
#       [https://en.wikipedia.org/wiki/Orthogonal_frequency-division_multiplexing]
# Channelizer algorithms available:
#   - Frequency domain
#   - Time domain
#   - Overlap
# Synthesizer algorithms available:
#   - Frequency domain
#   - Time domain
#   - Multichannel

# NOTE: A -channelizer- turns a broadband input into multiple narrowband outputs,
# while a -synthesizer- merges multiple narrowband inputs to one broadband output.
# at a signal-processing level, both of these require -filter banks-, but I'm 
# still trying to determine why a synthesizer needs a filter bank.
# See these links for an overview.
#   [https://en.wikipedia.org/wiki/Channelization_(telecommunications)]
#   [https://sci-hub.tw/https://doi.org/10.1016/B978-0-12-407682-2.00011-9]
#   [https://ieeexplore.ieee.org/document/8104959]

# MAC LAYER #


# NET LAYER #




