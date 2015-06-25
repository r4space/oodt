""" Zookeeper Config Pystache Class """
class ZK(object):

	def __init__ (self,DataDir="/tmp/zookeeper/data", Port=2181, maxClientCnxns=0,initLimit=5,syncLimit=2):
		self.Port=Port
		self.DataDir=DataDir
		self.maxClientCnxns=maxClientCnxns
		self.initLimit=initLimit
		self.syncLimit=syncLimit


	def DataDir(self):
		return DataDir

	def Port(self):
		return Port

	def maxClientCnxns(self):
		return maxClientCnxns

	def initLimit(self):
		return initLimit

	def syncLimit(self):
		return syncLimit
