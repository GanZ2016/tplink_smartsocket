import os
from subprocess import call
import time

#-------------------#
#change your device local address
addr = "192.168.1.132"
#-------------------#

#-------------------#
#how long you want to run (0.5 hour)
i = 120 
#-------------------#

#-------------------#
#what freq you want to run (min)
freq = 1 
#-------------------#


def run_python():
    cmd0 = "python tplink_smartplug.py -t " + addr + " -c power"
    call([cmd0], shell = True)

while i>0:
	run_python()
	time.sleep(freq*60)
	i = i -1
