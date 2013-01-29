#!/usr/bin/python

import socket
import sys
import time
import subprocess
import xmlrpclib
from pysnmp.entity.rfc3413.oneliner import cmdgen

class Poll:
	def __init__(self):
		f = open('./remote_lladdr', 'r')
		remote_lladdr = f.read()
		f.close()
		self.s = xmlrpclib.ServerProxy('http://[' + remote_lladdr + '%eth0.11]:8000')
		#print self.s.system.listMethods()

	def poll_rx(self):
		res = self.s.rx()
		return res

	def snmp_tx(self):
		cmdGen = cmdgen.CommandGenerator()

		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
			cmdgen.CommunityData('public'),
			cmdgen.UdpTransportTarget(('192.168.168.1', 161)),
			#'1.3.6.1.4.1.12919.6.8.0' <-- for inteno
			'1.3.6.1.4.1.890.1.5.8.46.117.2.1.7.1.4'
		)
		#return str(varBinds[0][1])[:-4] <-- for inteno
		return float(varBinds[0][1])

if __name__ == '__main__':
	run = Poll()
	rx = run.poll_rx() / 100
	tx = run.snmp_tx() / 100
	diff = float(tx) - float(rx)
	print diff
	print "0"
	print "0"
	print "0"