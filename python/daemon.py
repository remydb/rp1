#!/usr/bin/python
import socket
import sys
import subprocess
import time
import threading
import socket
import SocketServer
import xmlrpclib
import sched
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from pysnmp.entity.rfc3413.oneliner import cmdgen
from xml.dom.minidom import parseString
from string import split
from hashlib import sha224

class Authcls:
	auth_pass = "Tallgrass"
	dev = "eth0.11"

	def get_lladdrs(self):
		subprocess.call(["ping6", "-c4", "-I", self.dev, "ff02::1"], stdout=subprocess.PIPE)
		proc = subprocess.Popen(["ip", "-6", "neighbor", "show", "dev", self.dev], stdout=subprocess.PIPE)
		output = proc.stdout.read()
		ndlines = split(output, "\n")

		lladdrs = []
		for line in ndlines:
			lladdr = split(line, " ")
			lladdrs.append(lladdr[0])

		lladdrs.pop()
		return lladdrs

	def create_hashed_auth(self):
		proc = subprocess.Popen("ifconfig " + self.dev + " | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'", stdout=subprocess.PIPE, shell=True)
		own_lladdr = proc.stdout.read().rstrip()
		auth = self.auth_pass + " " + own_lladdr
		hashed_auth = sha224(auth).hexdigest() # we should also put a Nonce in here maybe?
		return hashed_auth

	def check_lladdr(self):
		f = open('./remote_lladdr', 'r')
		lladdr = f.read()
		f.close()
		s = xmlrpclib.ServerProxy('http://[' + lladdr + '%eth0.11]:8000')
		functimer = threading.Timer(30.0, self.check_lladdr)
	
		try:
			if s.heartbeat() == 1:
				print "Heartbeat success"
				functimer.start()
				return 1
		except:
			print "Heartbeat failed, retrying"
			time.sleep(5)
			try:
				if s.heartbeat() == 1:
					print "Heartbeat success on second attempt"
					functimer.start()
					return 1
			except:
				print "Heartbeat failed on second attempt, rerunning neighbour search"
				self.runloop()


	def runloop(self):
		lladdrs = self.get_lladdrs()
		ownhash = self.create_hashed_auth()
		auth_done = False
		functimer = threading.Timer(30.0, self.check_lladdr)

		while auth_done == False:
			for lladdr in lladdrs:
				try:
					s = xmlrpclib.ServerProxy('http://[' + lladdr + '%eth0.11]:8000')
					if s.auth(ownhash) == 1:
						print "Auth succeeded for " + lladdr
						auth_done == True
						f = open('./remote_lladdr', 'w')
						f.write(lladdr)
						f.close()
						functimer.start()
						return 1
					else:
						print "Auth failed for " + lladdr
						time.sleep(1)
				except:
					time.sleep(1)


class RequestHandler(SimpleXMLRPCRequestHandler):
    def __init__(self, req, addr, server):
    	self.client_ip = addr[0]
    	SimpleXMLRPCRequestHandler.__init__(self, req, addr, server)
    	self.rpc_paths = ('/RPC2',)

    def decode_request_content(self, data):
    	data = SimpleXMLRPCRequestHandler.decode_request_content(self, data)
    	doc = parseString(data)
    	ps = doc.getElementsByTagName('params')[0]
    	pdoc = parseString(
    		''' <param><value>
    		<string>%s</string>
    		</value></param>''' % (self.client_ip,))
    	p = pdoc.firstChild.cloneNode(True)
    	ps.insertBefore(p, ps.firstChild)
    	return doc.toxml()

class Polls:
	def auth(self, srcip, rcvdhash):
		check_auth = Authcls.auth_pass + " " + srcip.split('%')[0]
		hashed_check_auth = sha224(check_auth).hexdigest()
		if hashed_check_auth == rcvdhash:
			return 1
		else:
			return 0

	def heartbeat(self, srcip):
		return 1

	def rx(self, srcip):
		cmdGen = cmdgen.CommandGenerator()

		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
			cmdgen.CommunityData('public'),
			cmdgen.UdpTransportTarget(('192.168.168.1', 161)),
			'1.3.6.1.4.1.12919.6.9.0'
		)
		return str(varBinds[0][1])[:-4]

class Statserv(threading.Thread):
	def __init__(self):
		super(Statserv, self).__init__()
		p	=	subprocess.Popen(["ip addr show eth0 | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'"], stdout=subprocess.PIPE, shell=True)
		self.host	=	p.communicate()[0].rstrip() + '%eth0.11'
		self.port	=	32323

	def run(self):
		SocketServer.TCPServer.address_family = socket.AF_INET6
		server = SimpleXMLRPCServer(("::", 8000), requestHandler=RequestHandler, logRequests=0)
		server.register_introspection_functions()
		server.register_instance(Polls())

		# Run the server's main loop
		server.serve_forever()

if __name__ == '__main__':

	t = Statserv()

	t.daemon = False
	t.start()

	x = Authcls()
	x.runloop()

	#timer = threading.Timer(30.0, x.check_lladdr)
	#timer.start()