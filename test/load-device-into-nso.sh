#!/usr/bin/env ncs_cli 

config
load merge init_data/simdefaultauthgroup.xml
load merge init_data/devices/sim-isr-4451-1.xml
load merge init_data/devices/sim-isr-4451-2.xml
load merge init_data/devices/sim-catalyst-6840-1.xml
load merge init_data/devices/sim-catalyst-3850-1.xml
load merge init_data/devices/sim-catalyst-3850-2.xml
commit


