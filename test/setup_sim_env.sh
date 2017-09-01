#!/bin/bash

if [ -z "$PROJECTDIR" ]
then
	echo "Please set PROJECTDIR environment variable"
	exit 1
fi
if [ ! -e "$PROJECTDIR/init_data/devices" ]
then
	echo "Creating directory: $PROJECTDIR/init_data/devices"
	mkdir $PROJECTDIR/init_data/devices
fi
echo "___ Deleting local simulation netsim devices ___"
ncs-netsim delete-network
echo "___ Creating local simulation netsim devices ___"
ncs-netsim create-device cisco-ios sim-isr-4451-1
ncs-netsim add-device cisco-ios sim-isr-4451-2
ncs-netsim add-device cisco-ios sim-catalyst-6840-1
ncs-netsim add-device cisco-ios sim-catalyst-3850-1
ncs-netsim add-device cisco-ios sim-catalyst-3850-2
echo "___ Starting local simulation netsim devices ___"
ncs-netsim start
echo "___ Generating netsim device configuration files for NSO ___"
ncs-netsim ncs-xml-init sim-isr-4451-1 > $PROJECTDIR/init_data/devices/sim-isr-4451-1.xml
ncs-netsim ncs-xml-init sim-isr-4451-2 > $PROJECTDIR/init_data/devices/sim-isr-4451-2.xml
ncs-netsim ncs-xml-init sim-catalyst-6840-1 > $PROJECTDIR/init_data/devices/sim-catalyst-6840-1.xml
ncs-netsim ncs-xml-init sim-catalyst-3850-1 > $PROJECTDIR/init_data/devices/sim-catalyst-3850-1.xml
ncs-netsim ncs-xml-init sim-catalyst-3850-2 > $PROJECTDIR/init_data/devices/sim-catalyst-3850-2.xml
echo "___ Loading netsim device configurations into NSO ___"
$PROJECTDIR/test/load-device-into-nso.sh
echo "___ Syncing NSO with local simulation devices ___"
$PROJECTDIR/test/sync-dev.sh
