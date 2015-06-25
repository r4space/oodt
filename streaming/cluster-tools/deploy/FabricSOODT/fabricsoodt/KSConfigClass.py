""" Kafka Config Pystache Class """
class KS(object):

	def __init__ (self,	ID=0, Port=9092, Host="localhost",	AdvertisedHost=None, AdvertisedPort=None,	NetThreads=3,	IOThreads=8, TxBuffer=102400, RXBuffer=102400, ReqMax=104857600, LogDir="/tmp/kafka-logs", Partitions=1, ThreadsPerDD=1,	FlushDelayMessages=None, FlushDelayMS=None, LogRetentionHr=168,	LogRetentionB=None,	MaxLogSeg=10073741824,	LogCheckMS=300000,	EnableLogClean=False,ZC="localhost:2181",ZKTimeout=6000):
		self.ID=ID
		self.Port=Port
		self.Host=Host
		self.AdvertisedHost=AdvertisedHost
		self.AdvertisedPort=AdvertisedPort
		self.NetThreads=NetThreads
		self.IOThreads=IOThreads
		self.TxBuffer=TxBuffer
		self.RXBuffer=RXBuffer
		self.ReqMax=ReqMax
		self.LogDir=LogDir
		self.Partitions=Partitions
		self.ThreadsPerDD=ThreadsPerDD
		self.FlushDelayMessages=FlushDelayMessages
		self.FlushDelayMS=FlushDelayMS
		self.LogRetentionHr=LogRetentionHr
		self.LogRetentionB=LogRetentionB
		self.MaxLogSeg=MaxLogSeg
		self.LogCheckMS=LogCheckMS
		self.EnableLogClean=EnableLogClean
		self.ZC=ZC
		self.ZKTimeout=ZKTimeout
		
			
	def ID(self):
		return ID

	def Port(self):
		return Port

	def Host(self):
		return Host

	def AdvertisedHost(self):
		return AdvertisedHost

	def AdvertisedPort(self):
		return AdvertisedPort

	def NetThreads(self):
		return NetThreads

	def IOThreads(self):
		return IOThreads

	def TxBuffer(self):
		return TxBuffer

	def RXBuffer(self):
		return RXBuffer

	def ReqMax(self):
		return ReqMax

	def LogDir(self):
		return LogDir

	def Partitions(self):
		return Partitions

	def ThreadsPerDD(self):
		return ThreadsPerDD

	def FlushDelayMessages(self):
		return FlushDelayMessages

	def FlushDelayMS(self):
		return FlushDelayMS

	def LogRetentionHr(self):
		return LogRetentionHr

	def LogRetentionB(self):
		return LogRetentionB

	def MaxLogSeg(self):
		return MaxLogSeg

	def LogCheckMS(self):
		return LogCheckMS

	def EnableLogClean(self):
		return EnableLogClean

	def ZC(self):
		return ZC

	def ZKTimeout(self):
		return ZKTimeout
