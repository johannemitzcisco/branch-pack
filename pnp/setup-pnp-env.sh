#!/bin/bash

if [ "$PROJECTDIR" == "" ]; then
	echo "Please set PROJECTDIR env variable to the ncs run directory"
	exit 1
fi

PNPDEVICELOGSDIR=$PROJECTDIR/logs/pnp-devices
PNPSETUPDIR=$PROJECTDIR/pnp
PNPDAY0CONFIGDIR=$PNPSETUPDIR


getent passwd pnpsystem > /dev/null 2&>1

if [ $? -ne 0 ]; then
	echo creating user pnpsystem
	adduser -d /home/pnpsystem -g root -m -p pnpsystem -s /bin/bash pnpsystem
fi

if [ ! -d $PNPDEVICELOGSDIR ]; then 
	echo Creating directory $PNPDEVICELOGSDIR
	mkdir $PNPDEVICELOGSDIR;
fi
if [ ! -d $PNPDAY0CONFIGDIR ]; then 
	echo Creating directory $PNPDAY0CONFIGDIR
	mkdir $PNPDAY0CONFIGDIR;
fi

read -d '' nsocommand <<- EOF
configure
load merge $PNPSETUPDIR/pnpsettings.xml
commit
EOF

echo Running NSO comands:
echo "$nsocommand"
echo "$nsocommand" | ncs_cli -u admin 

read -d '' nsocommand <<- EOF
configure
load merge $PNPSETUPDIR/pnpsystemuser.xml
commit
EOF

echo Running NSO comands:
echo "$nsocommand"
echo "$nsocommand" | ncs_cli -u admin 
