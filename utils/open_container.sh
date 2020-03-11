#!/bin/bash
# Description: This script takes the name of a container as input. 
# First, it will show available grid list and wait for user input.
# After user provides the grid numbers, it will attempt to start containers on those grids
# Next, it will start "tmux" session with four panes. The organization of the panes are described later.
# The first grid number provided by the user will be opened on pane 0; second one on 1, and so on 
# Finally, the tmux session will be attached.    

if [ "$1" == "-h" ]; then  echo -e "Usage: `basename $0` [-h] [CONTAINER_ID: Max is 4] \n";  exit 0; fi

container=$1

availableGrids=`gridcli -l`
echo -ne "$availableGrids \n\n"

#grid number user Input
echo "Please enter the 2-digit grid numbers separated by space ie.01 11 19:"
IFS=' ' read -ra ID_array 


IP="" #initialize a variable to store the IPs of grids

for ID in "${ID_array[@]}"; do
    #fix digit issue with grid ID if exists
	if [ ${#ID} -lt 2 ] ; then ID="0${ID}";fi
    if [ ${#ID} -gt 2 ] ; then ID="${ID:0:2}";fi
    
	#Start Container
	cmd=`gridcli -gn grid$ID --start -i $container`
    echo -ne "$cmd \n\n\n\n"
    
    #get IP of each container
	cmd=`gridcli -gn grid$ID -ip`
	IP="$IP $cmd"
	
done

#make an IP array
IFS=' ' read -ra IP_array <<< "$IP"

#initiate tmux
tmux new-session -d 

#split window into four panes
# +---+---+
# | 0 | 1 |
# +---+---+
# | 2 + 3 +
# +---+---+
# Above order will change if the following sequences change
tmux split-window -h 
tmux split-window -t 0 -v 
tmux split-window -t 1 -v 
#End of tmux pane opening 


#send commands to tmux panes...
#loop through each IP
i=0; #for pane number
for ip in "${IP_array[@]}"; do
	#log in
	tmux send -t $i "sshpass -p kapilrocks ssh -XC root@$ip" ENTER;
	#connect eth
	tmux send -t $i 'ifconfig eth1 192.168.10.1' ENTER;
	#bring git repo
	tmux send -t $i "git clone https://github.com/dragonantijamming/dragonantijammer.git" ENTER;
	
	tmux send -t $i 'cd dragonradio' ENTER;
	#for convenience
	tmux send -t $i "echo -e \"This is grid${ID_array[$i]}\"" ENTER;
	
	((i++));
done
tmux select-pane -t 0


#Optional: Send commands to other panes....
# ... ... ...


#append last Session
tmux a



