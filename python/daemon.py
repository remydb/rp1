#!/usr/bin/python
import socket
import sys
import subprocess
import time
import socket
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from pysnmp.entity.rfc3413.oneliner import cmdgen

class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)

class Polls:
	def temp(self):
		return "TEMP"

	def rx(self):
		cmdGen = cmdgen.CommandGenerator()

		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
			cmdgen.CommunityData('public'),
			cmdgen.UdpTransportTarget(('192.168.168.1', 161)),
			'1.3.6.1.4.1.12919.6.9.0'
		)
		return "wut"
		# Check for errors and print out results
		if errorIndication:
			return errorIndication
		else:
			if errorStatus:
				return('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBinds[int(errorIndex)-1] or '?'
					)
				)
			else:
				for name, val in varBinds:
					return('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

	def tx(self):
		return "TXVAL"

class Statserv:
	def __init__(self):
		p	=	subprocess.Popen(["ip addr show eth0.11 | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'"], stdout=subprocess.PIPE, shell=True)
		self.host	=	p.communicate()[0].rstrip() + '%eth0.11'
		self.port	=	32323
		self.listen()

	def listen(self):
		SocketServer.TCPServer.address_family = socket.AF_INET6
		server = SimpleXMLRPCServer(("::", 8000), requestHandler=RequestHandler)
		server.register_introspection_functions()
		server.register_instance(Polls())

		# Run the server's main loop
		server.serve_forever()

if __name__ == '__main__':
	run = Statserv()
