from __future__ import print_function
'''
Used to deploy an instance of Streaming-OODT across a heterogenous cluster
Usage: python deploy.py [install|clean] [config_file] 
'''

#External imports
import sys
import os
import logging

#Setup logging

logger=logging.getLogger("fabricsoodt")
logger.setLevel(logging.DEBUG)
formatter=logging.Formatter("%(levelname)s:%(name)s:%(message)s")
FH = logging.FileHandler('./logs/SOODTInstall.log','w')
FH.setLevel(logging.DEBUG)
FH.setFormatter(formatter)
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
CH.setFormatter(formatter)
logger.addHandler(FH)
logger.addHandler(CH)

try:
	import fabric
	import configparser
	import pystache
except ImportError, e:
    logger.error("Error: {0}".format(e))
    print("Please install the necessary python modules: 'pip install --user -r requirements.txt'")
    sys.exit(1)

import fabricsoodt.operate


#Check correct calling
usage_string = "Usage: python deploy.py [ install | clean ] [ config_file ]" 

if len(sys.argv) < 3:
	logger.error("Error: Incorect call syntax")
	print(usage_string)
	sys.exit(1)

elif not os.path.exists(sys.argv[2]):
	pwd = os.getcwd()
	path_to_file = pwd + '/' + sys.argv[2]
	logger.error("Error: Configuration file: {}, does not exist".format(path_to_file))
	print(usage_string)
	sys.exit(1)
	
else:

	if sys.argv[1].lower() == "install":
		logger.info("> Begining install of SOODT")
		fabricsoodt.operate.install()
	
	elif sys.argv[1].lower() == "clean":
		logger.info("Cleaning SOODT install directories")
		fabricsoodt.operate.clean()
	
	elif sys.argv[1].lower() =='start':
		logger.info("Starting components")
		fabricsoodt.operate.start()
	
	elif sys.argv[1].lower() =='stop':
		logger.info("Stopping components")
		fabricsoodt.operate.stop()
	
	else:
		print("Error: Uncognised command")
		print(usage_string)
		sys.exit(1)
