""" Python script call all modules and reading the config file to deploy an instance of OODT accross a **heterogenous** cluster"""
#External imports
import sys 
import os
from getpass import getuser
from fabric.api import env, execute, roles, local, lcd, run
#from fabric.contrib.files import exists
#Packacge imports
import setup
import build
import distribute

def main():
	f = open("../logs/SOODT_install.log","w")
	print "\nRunning SOODT install application across cluster"
	f.write("\n\nRunning SOODT install application across cluster")

#Read Configuration
	if setup.python_uninstalled("configparser"):
		setup.pip_install("configparser")
	import configparser
	
	print "\nReading configuration file" + str(sys.argv[1])
	f.write("\n\nReading configuration file" + str(sys.argv[1]))

	config = configparser.ConfigParser()
	config.sections()
	config.read(str(sys.argv[1]))
	config.sections()
	CONFIGS = config['CONFIGS']
	SUDO = CONFIGS.getboolean('sudo')
	USER = CONFIGS['user']
	nodes = CONFIGS['nodes'].split(',')
	NODES=[]
	for i in nodes: NODES.append(i.strip())

#Get a download and install location	
	if CONFIGS.getboolean('localInstall'):
		destination = CONFIGS['destination']
	else:
		try:
			destination = os.mkdir(os.path.expanduser("~")+"/SOODT_Build_Area")
		except Exception:
			pass

#Download and untar each application, building if necessary too
	appnames = {}
	for app in config:
		if app == "DEFAULT" or app == "CONFIGS": continue

		url = config[app]['url']
		name = os.path.basename(config[app]['url'])
		fullname = destination+name
		appnames[app]=fullname

		#Try downloading up to 3 times
		for i in range(1,4):
			if os.path.isfile(destination + name):
				print "\n"+name + " already exists, skipping download stage."
				f.write("\n\n"+name + " already exists at " + destination + ",skipping download stage.")
				break
			else:
				print "\nDownloading " + app + " to " + destination
				f.write("\n\nDownloading " + app + " to " + destination)
				ret = setup.download(url, destination)
				if ret: 
					break
				else:
					print "\nFailed to download, trying again, (%d) attempts" %(i)
					f.write("\n\nFailed to download, trying again, (%d) attempts" %(i))

		#Extract, and if necessary build, applications
		print "\nApplication "+ app + " to be extracted from " + name + " to " + destination 
		f.write ("\n\nApplication "+ app + " to be extracted from " + name + " to " + destination)
	
		ret = build.extract(fullname, destination)
		print "Finished extraction with code: ", ret
		f.write("\n\nFinished extraction with code: " + str(ret))

		msg = [0,"Not building "+app]
		if config[app].getboolean('build'):
			try:
				sys.argv[2]
			except Exception:
				rebuild = False
			else:
				rebuild = True

			if rebuild == False:	#Not a rebuild, continue with install
				print "\nApplication "+ app + " to be build"
				f.write("\n\nApplication "+ app + " to be build")
				try:
					msg = build.build(app,fullname,SUDO, config[app].getboolean('test'))
				except KeyboardInterrupt:
					setup.clean_exit("Excited on keyboard interrupt",f)

			elif rebuild == True and sys.argv[2] == app:	#Is a rebuild of this app
				print "\nApplication "+ app + " to be rebuild"
				f.write("\n\nApplication "+ app + " to be rebuild. process will exit on completion")
				try:
					msg = build.build(app,fullname,SUDO, config[app].getboolean('test'))
				except KeyboardInterrupt:
					setup.clean_exit("Excited on keyboard interrupt",f)
				f.write("\n\nCompleted attampt at a rebuild of "+app)
				f.close()
				sys.exit("\n\nCompleted attampt at a rebuild of "+app)

			else:	#A rebuild has been requested but not of this app, continue
				continue

		if msg[0]==0:	
			print "\n\n"+msg[1]
			f.write("\n\n"+msg[1])
		else:
			print "\n\n"+msg[1]
			f.write("\n\n"+msg[1])
			setup.clean_exit(msg[1],f)


#Distribute and configure
	dist = setup.getos()
	env.roledefs = {'head':['localhost'], 'nodes':NODES} #Move to top of file when restructure above to use fabric instead of os and subprocess calls
	env.colorize_error = True
	env.user = USER 
	#Dependancies required excluding those required only for building specific applications
	ToQuery = [['subversion',1]]


	#Check ulimit -u is above 4096
	execute(distribute.ulimitCheck,roles=['nodes'])
	#Check env variables are set:
	execute(distribute.variablesCheck,roles=['nodes'])
	#Check all required dependancies are installed
	missing = execute(distribute.dependanciesCheck,ToQuery,dist,roles=['nodes'])
	if filter(lambda d: d !="",missing.values()):
		f.write("The following dependancies are missing on the deploy nodes, please install and re-runi: "+str(missing))
		setup.clean_exit("The following dependancies are missing on the deploy nodes, please install and re-run: "+str(missing),f)


	#Distribute Kafka
	if config['kafka'].getboolean('config'):
		pwd = local("pwd")
		print "\nReading Kafka configuration file"
		f.write("\n\nReading Kafka configuration file")
		Kconfig = configparser.ConfigParser()
		Kconfig.sections()
		Kconfig.read('../configs/kafka_config.ini')
		CLUSTER = Kconfig['CLUSTER']
		kservers = CLUSTER.getint('servers')
		kreplication = CLUSTER.getint('replication')
		kpartitions = CLUSTER.getint('partitions')
		ZDIR=CLUSTER['ZDIR'].strip()
		escZDIR=ZDIR.replace('/','\\/')
		Knodes = CLUSTER['nodes'].split(',')
		KNODES=[]
		for i in Knodes: KNODES.append(i.strip(" "))

		#Set $K_HOME remotely
		K_HOME = appnames['kafka'][:-4]+"/"
		print "K_HOME: ", K_HOME
		execute(distribute.remoteSetVar,"K_HOME="+K_HOME,hosts=KNODES)
		
		#Check required destination folders exists and if not create it on remote nodes
		for inode in KNODES:
			execute(distribute.ExistsCreate, destination, hosts=inode)
			execute(distribute.ExistsCreate, ZDIR, hosts=inode)
		
		#Transfer kafka files
		print "Transfering Kafka Files"
		f.write("\n\nTransfering Kafka Files")
		execute(distribute.transfer, appnames['kafka'][:-4] , destination ,hosts=KNODES)

		#Setup Zookeeper config file
		local("cp ../templates/zookeeper-template.properties ../templates/zookeeper.properties")
		#local("sed -i \"12s/.*/dataDir=\\/tmp\\/zookeeper\\/data\\//\" ../templates/zoo.cfg")#Set Zookeeper data directory
		local( "sed -i \"16s/.*/dataDir="+escZDIR+"/\" ../templates/zookeeper.properties")#Set Zookeeper data directory
		server=0
		for inode in Knodes:
			local("echo "+"\"server."+str(server)+"="+str(inode)+":2888:3888\""+" >> ../templates/zookeeper.properties")#List servers
			server += 1
		
		#Distribute Zookeeper Config:
		print "Transfering Zookeeper configs"
		f.write("\n\nTransfering Zookeeper confis")
		server=0
		for inode in Knodes:
			execute(distribute.transfer, pwd+"../templates/zookeeper.properties" , K_HOME+"config/zookeeper.properties" ,hosts=inode)#Push config file
			local("echo "+str(server)+" > ../templates/myid")#Create myid file
			execute(distribute.transfer, pwd+"../templates/myid" , ZDIR ,hosts=inode)#Push myid file
			server+=1
		
		#Setup Kafka config files
		zc = "zookeeper.connect="
		for inode in Knodes:
			zc=zc+str(inode)+":2181,"
		zc=zc[:-1]
		server=0
		print "Transfering Kafka configs"
		f.write("\n\nTransfering Kafka confis")
		for inode in Knodes:
			local("cp ../templates/kafka-server-template.properties	../templates/kafka-server"+str(server)+".properties")
			local("sed -i \"20s/.*/brocker.id="+str(server)+"/\" ../templates/kafka-server"+str(server)+".properties")#Set brokerID
			local("sed -i \"28s/.*/host.name="+str(inode)+"/\" ../templates/kafka-server"+str(server)+".properties")#Set hostname
			local("sed -i \"118s/.*/"+zc+"/\" ../templates/kafka-server"+str(server)+".properties")#Set ZKconnect
			execute(distribute.transfer, pwd+"../templates//kafka-server"+str(server)+".properties" , K_HOME+"config/server.properties", hosts=inode)#Push kafkaserver.properties
			server += 1
		
		print "K_HOME: "+K_HOME
		#Add execution writes to scripts
		print "CMODding"
		f.write("\n\nCHMODDING")
		execute(distribute.chmodFolder,K_HOME+"/bin/",hosts=Knodes)

		#Start Kafka Cluster
#		distribute.startKafka(KNODES)

#Test installation
		print "I got here"
	
	
	
	print "Finished"
	f.write("\n\nFinished")
	f.close()

if __name__ == "__main__": main()

