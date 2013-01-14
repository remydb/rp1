#!/usr/bin/python

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from string import split
from hashlib import sha224

#########################################
# Discover all IPv6 linklocal addresses #
#########################################
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

###########################################
# create a hash containing:		  #
#	1: the pre-shared secret password #
#	2: our own LinkLocal address      #
###########################################
def create_hashed_auth(auth_pass, dev):
	proc = Popen("ifconfig " + dev + " | grep -oE 'fe80::[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*:[0-9,a-f]*'", stdout=PIPE, shell=True)
	own_lladdr = proc.stdout.read().rstrip()
	auth = auth_pass + " " + own_lladdr
	hashed_auth = sha224(auth).hexdigest() # we should also put a Nonce in here maybe?
	return hashed_auth

###########################################
# check a hash containing:		  #
#	1: the pre-shared secret password #
#	2: our own LinkLocal address      #
###########################################
def check_hashed_auth(hashed_auth, auth_pass, remote_lladdr):
	check_auth = auth_pass + " " + remote_lladdr
	hashed_check_auth = sha224(check_auth).hexdigest()
	if hashed_check_auth == hashed_auth:
		return 1
	else:
		return 0


#########################################
# MAIN					#
#########################################
auth_pass = "Tallgrass"
dev = "eth1"
remote_lladdr = "fe80::a00:27ff:fe4f:3a31"

hashed_auth = create_hashed_auth(auth_pass, dev)

lladdrs = get_lladdrs(dev)
for lladdr in lladdrs:
	result = check_hashed_auth(hashed_auth, auth_pass, remote_lladdr)
	print result
