#!/bin/bash
#source this file to load the project environment

if [ ! -e ncs.conf ]; then
	echo "Please source this file from the ncs run directory (project directory)"
	exit 1
fi

export PROJECTDIR=$PWD
echo Settting environment, PROJECTDIR=$PROJECTDIR
alias nso-cli="ncs_cli -u admin"


