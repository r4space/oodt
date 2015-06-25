""" This package enables easy installatin of Streeming OODT accross a homogenous cluster 

Package depends on:
	fabric 

packge includes:
	steup
	building
	distributing

"""
#Local module imports
import setup

#Check public modules are available for import
#Check for: 
#	fabric
#	configparser
if setup.uninstalled("fabric"):
	setup.install("fabric")
if setup.uninstalled("configparser"):
	setup.install("configparser")
#if setup.uninstalled("yaml"):
#	setup.install("pyyaml")




