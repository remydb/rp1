#!/usr/bin/python
import socket
import sys
import subprocess
import time
import threading
import socket
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from pysnmp.entity.rfc3413.oneliner import cmdgen

class Find:
	def __init__(self):
		self.auth_pass = "Tallgrass"
		self.dev = "eth0.11"

	def get_lladdrs(self):
		subprocess.call(["ping6", "-c4", "-I", self.dev, "ff02::1"], stdout=subprocess.PIPE)
		proc = subprocess.Popen(["ip", "-6", "neighbor", "show", "dev", dev], stdout=subprocess.PIPE)
		output = proc.stdout.read()
		ndlines = split(output, "\n")

		lladdrs = []
		for line in ndlines:
			lladdr = split(line, " ")
			lladdrs.append(lladdr[0])

		lladdrs.pop()
		return lladdrs

	def create_hashed_auth(self):
		proc = subprocess.Popen("ifconfig " + self.dev + " | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'", stdout=PIPE, shell=True)
		own_lladdr = proc.stdout.read().rstrip()
		auth = self.auth_pass + " " + own_lladdr
		hashed_auth = sha224(auth).hexdigest() # we should also put a Nonce in here maybe?
		return hashed_auth

	def check_hashed_auth(self, hashed_auth, auth_pass, remote_lladdr):
		check_auth = self.auth_pass + " " + remote_lladdr
		hashed_check_auth = sha224(check_auth).hexdigest()
		if hashed_check_auth == hashed_auth:
			return 1
		else:
			return 0

	def runloop(self):
		lladdrs = self.get_lladdrs()
		ownhash = self.create_hashed_auth()

		for lladdr in lladdrs:
			s = xmlrpclib.ServerProxy('http://[' + lladdr + '%eth0.11]:8000')
			if s.auth(ownhash) == 1:
				return lladdr


class RequestHandler(SimpleXMLRPCRequestHandler):
    def __init__(self, req, addr, server):
       self.client_ip = addr
       SimpleXMLRPCRequestHandler.__init__(self, req, addr, server)
       self.rpc_paths = ('/RPC2',)
    # def decode_request_content(self, data):
    #    data = SimpleXMLRPCRequestHandler.decode_request_content(self, data)
    #    from xml.dom.minidom import parseString
    #    doc = parseString(data)
    #    ps = doc.getElementsByTagName('params')[0]
    #    pdoc = parseString(
    #         ''' <param><value>
    #             <string>%s</string>
    #             </value></param>''' % (self.client_ip,))
    #    p = pdoc.firstChild.cloneNode(True)
    #    ps.insertBefore(p, ps.firstChild)
    #    return doc.toxml()

class Polls:
	def auth(self, rcvdhash):
		print rcvdhash
		print RequestHandler.client_ip

	def rx(self):
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
		self.host	=	p.communicate()[0].rstrip() + '%eth0'
		self.port	=	32323
		#self.listen()

	def run(self):
		SocketServer.TCPServer.address_family = socket.AF_INET6
		server = SimpleXMLRPCServer(("::", 8000), requestHandler=RequestHandler)
		server.register_introspection_functions()
		server.register_instance(Polls())

		# Run the server's main loop
		server.serve_forever()

if __name__ == '__main__':
	#findcls = Find()
	#findcls.

	t = Statserv()

	t.daemon = False
	t.start()
	print t.isAlive()


