''' Module containing clean(), install(). start(), stop() '''
#External imports
import logging
import sys
import fabric.utils
import fabric.contrib.files
import fabric.contrib.console

#Package imports
import fabricsoodt
import fabricsoodt.setup
import fabricsoodt.build
import fabricsoodt.distribute
import fabricsoodt.start
import fabricsoodt.stop

logger = logging.getLogger('fabricssodt.operate')
logging.getLogger("paramiko").setLevel(logging.WARNING)

def clean():
	#Returns the contents of provided ini file as a dictionary of dictionaries
	fabric.api.local("rm -r ./logs/*")
	fabric.api.local("rm -r ./fabricsoodt/templates/myid")
	fabric.api.local("rm -r ./fabricsoodt/templates/*.properties")
	fabric.api.local("rm -r ./downloads/*")

def start():
	''' Start components based on config file requests and logical order '''
	#Returns the contents of provided ini file as a dictionary of dictionaries
	configuration = fabricsoodt.setup.readconfig(str(sys.argv[2]))
	logger.info("\n> Reading configuration file: {0}".format(sys.argv[2]))


	#Create an entry in configuration libraries contaning app specific IPs in a python list
	for app in configuration:
		if app == "CONFIGS" or app == "DEFAULT": continue
		nodeIPs = map(lambda z: z.strip(" "), configuration[app]['nodes'].split(","))
		configuration[app]['NODES']=nodeIPs 

	if configuration['KAFKA']['start']:
		logger.info("\n> Starting Kafka")
		fabricsoodt.start.startupKafka(configuration['KAFKA'])

#	if configuration['MESOS']['start']:
#		logger.info("\n> Starting Mesos")
#		fabricsoodt.start.startupMesos(configuration['MESOS'])

def stop():
	''' Stop components based on config file requests and logical order '''
	#Returns the contents of provided ini file as a dictionary of dictionaries
	configuration = fabricsoodt.setup.readconfig(str(sys.argv[2]))
	logger.info("\n> Reading configuration file: {0}".format(sys.argv[2]))


	#Create an entry in configuration libraries contaning app specific IPs in a python list
	for app in configuration:
		if app == "CONFIGS" or app == "DEFAULT": continue
		nodeIPs = map(lambda z: z.strip(" "), configuration[app]['nodes'].split(","))
		configuration[app]['NODES']=nodeIPs 

	if not configuration['KAFKA']['start']:
		logger.info("\n> Stopping Kafka")
		fabricsoodt.stop.stopKafka(configuration['KAFKA'])

#	if not configuration['MESOS']['start']:
#		logger.info("\n> Stopping Mesos")
#		fabricsoodt.stop.stopMesos(configuration['MESOS'])

def install():
# INITIALISATION 
#------------------------------------------

	#Returns the contents of provided ini file as a dictionary of dictionaries
	configuration = fabricsoodt.setup.readconfig(str(sys.argv[2]))
	logger.info("\n> Reading configuration file: {0}".format(sys.argv[2]))
	
	#Setup Fabric fabric.api.envs
	fabric.api.env.colorize_error = True
	fabric.api.env.user = configuration['CONFIGS']['user']
	fabric.api.env.roledefs = {'login':['localhost']}
	
	allIPs = set()
	for app in configuration:
		if app == "CONFIGS" or app == "DEFAULT": continue
		nodeIPs = map(lambda z: z.strip(" "), configuration[app]['nodes'].split(","))
		fabric.api.env.roledefs[app+'nodeIPs']=nodeIPs
		configuration[app]['NODES']=nodeIPs #Create an entry contaning the IPs in a python list
		[allIPs.add(x) for x in nodeIPs] #Create an ALLnodesIPs list
	fabric.api.env.roledefs['ALLnodesIPs']=allIPs


	#Set local env variables:
	fabric.api.execute(fabricsoodt.setup.setEnvs, configuration['CONFIGS']['envvars'], configuration['CONFIGS']['user'], roles=['login'])

#DOWNLOADS
#------------------------------------------
	pwd = fabric.api.local("pwd",capture=True)
	downloads = pwd+"/downloads/"
	
	dList = []
	for app in configuration:
		if app == "CONFIGS" or app == "DEFAULT": continue
	
		if fabric.api.execute(fabricsoodt.setup.download, configuration[app]['url'] , downloads, roles=['login']):
			logger.info("\n> Downloaded: {0} to {1}".format(app,downloads))

		else:
			logger.error("\n> Failed to download{0}".format(app))
			if not fabric.contrib.console.confirm("Do you wish to continue with out installing {0}".format(app)):
				fabric.api.abort("Aborting at users request")
			else:
				logger.info("\n> Continuing without {0}".format(app))
				dList.appen(app)

	for i in dList: del configuration[i]

#EXTRACT and BUILD
#------------------------------------------
	for app in configuration:
		if app == "CONFIGS" or app == "DEFAULT": continue

		tarPath = downloads+configuration[app]['url'].split('/')[-1:][0]
		#Extract returns the resulting folder name, capture to configuration
		configuration[app]['folderName'] = fabricsoodt.build.extract(tarPath, downloads)
		#Set Application HOME path
		configuration[app]['HOME'] =configuration['CONFIGS']['destination']+configuration[app]['folderName'] 

		if configuration[app]['build']:
			#Setup required environment variables
			fabric.api.execute(fabricsoodt.setup.setEnvs, configuration[app]['envvars'], configuration['CONFIGS']['user'],roles=['login'])
			
			#Run build
			msg = fabricsoodt.build.build(app,tarPath,configuration['CONFIGS']['sudo'], configuration[app]['test'])
			logger.info(msg)
		else:
			logger.info("\n> End build stage")

#DISTRIBUTE and CONFIGURE
#------------------------------------------

###################Commented out for future use ##################

#Dependancies are currently ensured/checked for in 3 manners:
# - The readme requires basics for install
# - If a build is requested that build function ensures that application's dependancies are met
# - This currently commented out section provides a means for additional packages to be installed, for instance a need for svn is indicated but currently unused.  To activate uncomment the following lines and provide the apt-get / yum recognisable names of dependancies in list ToQuery 


#	ToQuery = [['subversion',1]]
#	missing = execute(distribute.dependanciesCheck,ToQuery,setup.getos(),roles=['ALLnodesIPs'])
#	if filter(lambda d: d !="",missing.values()):
#		logger.error("The following dependancies are missing on the deploy nodes, please install and re-run: {}".format(str(missing)))
#		fabric.utils.abort("Aborting due to missing dependancies on remote nodes")

###################################################################

	#Check ulimit -u is above 4096
	fabric.api.execute(fabricsoodt.distribute.ulimitCheck,roles=['ALLnodesIPs'])
	#Check fabric.api.env variables are set:
	#fabric.api.execute(fabricsoodt.distribute.variablesCheck,roles=['ALLnodesIPs'])
	#Check destination folder exists
	destination = configuration['CONFIGS']['destination']
	fabric.api.execute(fabricsoodt.distribute.existsCreate,destination,roles=['ALLnodesIPs'])

	for app in configuration:
		if app == "CONFIGS" or app == "DEFAULT": continue

		#Distribute application
		source  = downloads+configuration[app]['folderName']
		logger.info("\n> Transfering {0} to nodes: {1}".format(source,destination)) 
		fabric.api.execute(fabricsoodt.distribute.transfer,source,destination,roles=[app + "nodeIPs"])
	
		#Distribute configuration files
		if configuration[app]['config']:
			fabric.api.execute(fabricsoodt.distribute.configure,app,configuration[app],roles=[app + "nodeIPs"])
		
		logger.info("\n> Completed {} configuration".format(app))


	#Start up instalation
	#Test installation

	logger.info("\n> SOODT deployment completed")
	logger.info("\n ############# END ##############")

