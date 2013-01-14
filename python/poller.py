#!/usr/bin/python2

import socket
import sys
import time

class Poll:
	def __init__(self):
		try:
			polltype	=	sys.argv[0]
		except:
			'''do nothing'''

	def connect(self):
		HOST = 'fe80::201:2eff:fe47:26d2%eth0.11'	# The remote host
		PORT = 32323			# The same port as used by the server
		s = None
		for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
			af, socktype, proto, canonname, sa = res
			try:
				s = socket.socket(af, socktype, proto)
			except socket.error as msg:
				s = None
				continue
			try:
				s.connect(sa)
			except socket.error as msg:
				s.close()
				s = None
				continue
			break
		if s is None:
			print 'could not open socket'
			sys.exit(1)
		s.sendall('Hello, world')
		data = s.recv(1024)
		s.close()
		print 'Received', repr(data)

if __name__ == '__main__':
	run = Poll()
	run.connect()