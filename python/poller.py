#!/usr/bin/python

import socket
import sys
import time
import xmlrpclib

class Poll:
	def __init__(self):
		self.s = xmlrpclib.ServerProxy('http://[fe80::201:2eff:fe47:26d2%eth0.11]:8000')
		#print self.s.system.listMethods()

	# def poll_temp(self):
	# 	res = self.s.temp()	
	# 	print res	

	def poll_rx(self):
		res = self.s.rx()
		print res

	# def poll_tx(self):
	# 	res = self.s.tx()
	# 	print res

if __name__ == '__main__':
	run = Poll()
	func = getattr(run, sys.argv[1])
	print func
	if(callable(func)):
		func()
	else:
		print "Argument is not a valid poll command!"
