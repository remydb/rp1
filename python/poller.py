#!/usr/bin/python

import socket
import sys
import time
import subprocess
import xmlrpclib

class Poll:
	def __init__(self):
		self.s = xmlrpclib.ServerProxy('http://[fe80::201:2eff:fe47:26d2%eth0]:8000')
		#print self.s.system.listMethods()

	# def poll_temp(self):
	# 	res = self.s.temp()	
	# 	print res	

	def poll_auth(self):
		p	=	subprocess.Popen(["ip addr show eth0 | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'"], stdout=subprocess.PIPE, shell=True)
		self.host	=	p.communicate()[0].rstrip()
		res = self.s.auth(self.host)

	def poll_rx(self):
		res = self.s.rx()
		print res

	# def poll_tx(self):
	# 	res = self.s.tx()
	# 	print res

if __name__ == '__main__':
	run = Poll()
	func = getattr(run, sys.argv[1])
	if(callable(func)):
		func()
	else:
		print "Argument is not a valid poll command!"
