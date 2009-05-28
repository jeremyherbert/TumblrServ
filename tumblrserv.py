#!/usr/bin/env python

##    tumblrserv.py implements a Tumblr (http://www.tumblr.com) markup parsing
##    engine and compatible webserver.
##
##    Version: 0.2 final
##
##    Copyright (C) 2009 Jeremy Herbert
##    Contact mailto:jeremy@jeremyherbert.net
##
##    This program is free software; you can redistribute it and/or
##    modify it under the terms of the GNU General Public License
##    as published by the Free Software Foundation; either version 2
##    of the License, or (at your option) any later version.
##    
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##    
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
##    02110-1301, USA.

import os, sys, ftplib, yaml, cherrypy, re, urllib2

from src.post_classes import *
from src import json
from src.constants import *
from src.support import *
from src.net import *
from src.server import *

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video', 'Audio', 'Conversation']

args_dict = {
    'autoreload': 0, # Whether to add the meta refresh tag
    'publish': False, # Whether to push the new theme data to tumblr
    'data_source': DATA_LOCAL, # Whether to use local data in the theme
}

########################################

# take the arguments and place them in a mutable list 
arguments = sys.argv

# if the script has been run with the interpreter prefix, get rid of it
if arguments[0] == 'python' or arguments[0] == 'ipython' \
or arguments[0] == 'python2.5': 
    arguments.pop(0)

# pop off the script name
arguments.pop(0)

# load the configuration file
config_path = 'data/config.yml'
if contains(arguments, '--config'):
    if os.path.exists(next_arg(arguments, '--config')):
        config_path = next_arg(arguments, '--config')

config = get_config(config_path)

# now we check if there are any data processing flags
if contains(arguments, '--pull-data'):
    # call pull_data with the argument after the flag
    pull_data( next_arg(arguments, '--pull-data') )

if contains(arguments, '--theme'):
    if not os.path.exists("themes/" + next_arg(arguments, '--theme') + '.thtml'):
        err_exit("The theme file %s.thtml does not exist in the themes\
 directory." % next_arg(arguments, '--theme'))
    config['defaults']['theme_name'] = next_arg(arguments, '--theme')

if contains(arguments, '--publish'):
    if not has_keys(config['publishing_info'], \
     ( 'url', 'username', 'password' )): 

        err_exit('The configuration file is missing some critical publishing\
 information. Please make sure you have specified your url, username and\
 password.')
 
    publish_theme(config['publishing_info']['url'],\
     config['publishing_info']['username'],\
     config['publishing_info']['password'],\
     get_markup('themes/%s.thtml' % config['defaults']['theme_name']))
    
if contains(arguments, '--do-nothing'):
    config['optimisations']['do_nothing'] = True
    
# start the server up
cherrypy.config.update('data/cherrypy.conf')
cherrypy.quickstart(TumblrServ(config), '/')