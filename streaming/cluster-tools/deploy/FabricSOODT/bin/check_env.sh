#!/bin/bash

if [ -z $JAVA_HOME ]; then

	if hash java 2>/dev/null; then
		path=`which java`
		echo "export JAVA_HOME=$path" >> /home/$USER/.bash_profile
	else
		echo "Java is not installed please install"
		exit 1
	fi

fi

if [ -z $M2_HOME ]; then

	if hash mvn 2>/dev/null; then
		path=`which mvn`
		echo "export M2_HOME=$path" >> /home/$USER/.bash_profile
	else
		echo "Maven is not installed please install"
		exit 1
	fi

fi

exit 0


