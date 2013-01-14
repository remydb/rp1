#!/usr/bin/python2
import socket
import sys
import subprocess
import time

class Statserv:
	def __init__(self):
		p	=	subprocess.Popen(["ip addr show eth0.11 | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'"], stdout=subprocess.PIPE, shell=True)
		self.host	=	p.communicate()[0].rstrip() + '%eth0.11'
		self.port	=	32323
		self.listen()


	def listen(self):
		if not socket.has_ipv6:
			raise Exception("the local machine has no IPv6 support enabled")

		addrs = socket.getaddrinfo(self.host, self.port, socket.AF_INET6, socket.SOCK_STREAM)
		# example output: [(23, 0, 6, '', ('::1', 10008, 0, 0))]
		if len(addrs) == 0:
			raise Exception("there is no IPv6 address configured for localhost")
		entry0 = addrs[0]
		sockaddr = entry0[-1]
		s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		s.bind(sockaddr)
		s.listen(1)
		print "server opened socket connection:", s, ", address: '%s'" % sockaddr[0]
		conn, addr = s.accept()
	
		time.sleep(1)
		print 'Server: Connected by', addr
		while True: # answer a single request
			data = conn.recv(1024)
			print data
		conn.close()
		s.close()
		quit()

if __name__ == '__main__':
	run = Statserv()
