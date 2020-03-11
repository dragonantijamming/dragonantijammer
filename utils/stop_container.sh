#!/bin/bash
# Desc: This script takes grid number as input.
# First, it will kill all tmux sessions.
# Finally, if the user has proper authorization, it will stop 
# the containers running on those grids  
# If the user don't provide any grid number, it will attepmt to stop
# all containers running on grid 1-19.

#stop all tmux session
tmux kill-server

#make an array of user provided grid#
IFS=' ' read -ra ID_array <<< "$@"

# if no grid# provided then make a sequence for all grids
if [ $# == 0 ]; then ID_array=($(seq 0 1 19));fi

#loop through all grid
for ID in "${ID_array[@]}"; do 
	#fix grid#
	if [ ${#ID} -lt 2 ] ; then ID="0${ID}";fi
	if [ ${#ID} -gt 2 ] ; then ID="${ID:0:2}";fi
	
	#stop gird
	cmd=`gridcli -gn grid$ID --stop`
	echo -ne "$cmd \n"
done
