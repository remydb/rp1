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

class Find:
	def get_lladdrs(dev):
		call(["ping6", "-c4", "-I", dev, "ff02::1"], stdout=PIPE)
		proc = Popen(["ip", "-6", "neighbor", "show", "dev", dev], stdout=PIPE)
		output = proc.stdout.read()
		ndlines = split(output, "\n")

		lladdrs = []
		for line in ndlines:
			lladdr = split(line, " ")
			lladdrs.append(lladdr[0])

		lladdrs.pop()
		return lladdrs

	def create_hashed_auth(auth_pass, dev):
		proc = Popen("ifconfig " + dev + " | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'", stdout=PIPE, shell=True)
		own_lladdr = proc.stdout.read().rstrip()
		auth = auth_pass + " " + own_lladdr
		hashed_auth = sha224(auth).hexdigest() # we should also put a Nonce in here maybe?
		return hashed_auth

	def check_hashed_auth(hashed_auth, auth_pass, remote_lladdr):
		check_auth = auth_pass + " " + remote_lladdr
		hashed_check_auth = sha224(check_auth).hexdigest()
		if hashed_check_auth == hashed_auth:
			return 1
		else:
			return 0

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
		return str(varBinds[0][1])[:-4]

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
	rem_ip = Find()
	run = Statserv()
