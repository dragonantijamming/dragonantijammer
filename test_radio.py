# Setup script for DragonRadio
# Handles the radio setup as detailed in basic-dr.py
import argparse
import asyncio
from concurrent.futures import CancelledError
import IPython
from itertools import chain,cycle,starmap
import logging
import os
import random
import signal
import sys

import dragonradio
import dragon.radio

def main():
	config = dragon.radio.Config()
	
	parser = argparse.ArgumentParser(description='Run dragonradio.',
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	config.addArguments(parser)
	parser.add_argument('-n', action='store', type=int, dest='num_nodes',
		default=2,
		help='set number of nodes in network')
	parser.add_argument('--aloha', action='store_true', dest='aloha',
		default=False,
		help='use slotted ALOHA MAC')
	parser.add_argument('--interactive',
		action='store_true', dest='interactive',
		help='enter interactive shell after radio is configured')
	parser.add_argument('--cycle-tx-gain', action='store',
		choices=['sequential', 'discontinuous', 'random'],
		help='enable TX gain cycling')
	parser.add_argument('--cycle-tx-gain-period', type=float,
		default=10,
		help='TX gain cycling period')

	# Parse arguments
	try:
		parser.parse_args(namespace=config)
	except SystemExit as ex:
		return ex.code
	
	logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
		level=config.loglevel)
	
	if config.log_directory:
		config.log_sources += ['log_recv_packets','log_sent_packets','log_events']
	
	# Create radio object
	radio = dragon.radio.Radio(config)

	# Configure MAC objects
	nslots = 10
	nchannels = len(radio.getChannels())
	sched = np.array([1,2,3,1,2,3,1,2,3,1]) # nchannels x nslots array
	schedarray = []
	for i in range(0,nchannels):
		schedarray.append(sched)
	# schedarray is now a list of arrays: [ array([1,2,3...]), array([1,2,3...]), ... ]

	schedstack = np.vstack(sched) # Turn the list of arrays into a vertical stack of the arrays
	# => array([ [1,2,3...],
	#			 [1,2,3...],
	#			 ...
	#			 [1,2,3...] ])

	# This calls configureTDMA() and installs the TDMA schedule
	radio.installMACSchedule(schedstack)

	#
	# Start IPython shell if we are in interactive mode. Otherwise, run the
	# event loop.
	#
	if config.interactive:
		IPython.embed()
	else:
		loop = asyncio.get_event_loop()

		if config.log_snapshots != 0:
		loop.create_task(radio.snapshotLogger())

		if config.cycle_tx_gain is not None:
			loop.create_task(cycle_tx_gain(radio,
				config.cycle_tx_gain_period,
				cycle_algorithm(config.cycle_tx_gain)))

		for sig in [signal.SIGINT, signal.SIGTERM]:
			loop.add_signal_handler(sig, cancel_loop)

		try:
			loop.run_forever()
		finally:
			loop.close()

	return 0

if __name__=='__main__':
	main()

