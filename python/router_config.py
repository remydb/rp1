#!/usr/bin/python

###################################################################
# Do not redistribute this example file without deleting/editing: #
# switch = 'whatever'						  #
# username = 'whatever'						  #
# password = 'whatever'						  #
###################################################################  

import mlx_config_lib

####################################################################### Example usage ################################################################################################

switch = 'router'
username = 'stefan'
password = None

	mlx_config_lib.add_even(switch, username, password, snakerange)
	mlx_config_lib.port_up_bringer(switch, username, password, snakerange)
	raw_input('Press any key to continue')
	mlx_config_lib.port_down_bringer(switch, username, password, snakerange)
	mlx_config_lib.remove_vlans(switch, username, password)
