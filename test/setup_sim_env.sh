#!/bin/bash

if [ -z "$PROJECTDIR" ]
then
	echo "Please set PROJECTDIR environment variable"
	exit 1
fi
ncs-netsim delete-network
ncs-netsim create-device cisco-ios asr-1
#ncs-netsim add-device cisco-ios asr-2
#ncs-netsim add-device cisco-ios isr-4451-1
#ncs-netsim add-device cisco-ios isr-4331-1
#ncs-netsim add-device cisco-ios isr-4331-2
#ncs-netsim add-device cisco-ios catalyst-3850-1
ncs-netsim start
ncs-netsim ncs-xml-init asr-1 > $PROJECTDIR/init_data/devices/asr-1.xml
#ncs-netsim ncs-xml-init asr-2 > $PROJECTDIR/init_data/devices/asr-2.xml
#ncs-netsim ncs-xml-init isr-4451-1 > $PROJECTDIR/init_data/devices/isr-4451-1.xml
#ncs-netsim ncs-xml-init isr-4331-1 > $PROJECTDIR/init_data/devices/isr-4331-1.xml
#ncs-netsim ncs-xml-init isr-4331-2 > $PROJECTDIR/init_data/devices/isr-4331-2.xml
#ncs-netsim ncs-xml-init catalyst-3850-1 > $PROJECTDIR/init_data/devices/catalyst-3850-1.xml
$PROJECTDIR/test/load-device-into-nso.sh
$PROJECTDIR/test/sync-dev.sh
