#!/bin/bash
# Ensure running as root; possibly not necessary?
#if [ ! `id -un` = "root" ]; then
#	echo "Must run as root."
#	exit 1
#fi

# Setup sockets
SOCKETS="1:Powerheads 2:Canister 3:Skimmer"
for i in $SOCKETS; do
	num=`echo $i | awk -F: '{print$1}'`
	name=`echo $i | awk -F: '{print$2}'`
	clear
	echo "About to configurre Socket: $num, for Function: $name"
	echo
	echo "Plug the sockets you want assigned to this channel,"
	echo "and ensure they're flashing (in learn mode.)"
	echo
	echo "Press [ENTER] when ready:"
	read DUMMY
	echo
	echo "Configuring Socket(s) Number $num..."
	./switch $num on
	sleep 2
	echo "Done."
	sleep 2
done
