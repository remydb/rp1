#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2013, University of Amsterdam
#    Contact: 	stefan.plug@os3.nl
#		remy.deboer@os3.nl
#
#	This library is used with Exscript (https://github.com/knipknap/exscript/wiki)
#
	
#!/usr/bin/python

import time
import sys
import re
from Exscript import Account
from Exscript.protocols import SSH2
from Exscript.util.match import first_match
from Exscript.util.match import any_match

############################################## sub functions ####################################################################

def login(switch, username, password):
	conn = SSH2()
	#conn.debug = 0			#debugging info 0-5
	conn.stdout = sys.stdout	#To get line-by-line input/output from the switch
	conn.connect(switch)
	conn.login(Account(username, password))
	return conn

def port_status_check (port, conn):
	conn.execute('show interfaces brief '+ port)
	Link = first_match(conn, r'(Disab)')
	if Link == 'Disab':
		return 1
	Link = first_match(conn, r'(Empty)')
	if Link == 'Empty':
		return 2
	Link = first_match(conn, r'(Down)')
	if Link == 'Down':
		return 3
	Link = first_match(conn, r'(Up)')
	if Link == 'Up':
		Port_State = first_match(conn, r'(Forward)')
		if Port_State == 'Forward':
			return 4
		#There should be other possibilities than Port_State=Forward right?
	return 0


############################################## Main callable functions ####################################################################

def port_down_bringer(switch, username, password):

	conn = login(switch, username, password)
	conn.execute('configure terminal')
	conn.set_prompt(r'(config-if)')
	for port in snakearray:
		conn.execute('interface ' + port)
		conn.execute('disable')
	conn.set_prompt()
	conn.execute('quit')


