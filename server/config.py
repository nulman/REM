# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
server config file
'''
from os.path import abspath, dirname, exists, join as join_path

#experiments_root_dir is the initial directory to start the file browser in
#it will default to the server location
experiments_root_dir = dirname(abspath(__file__))
if exists(join_path(experiments_root_dir, 'experiments')):
    experiments_root_dir = join_path(experiments_root_dir, 'experiments')
config = dict(
              port = 5000,
              experiment_root_dir = experiments_root_dir,
              debug = True,
              hostname = '0.0.0.0',
              #the SECRET_KEY is required, without it you cant have sessions.
              SECRET_KEY = 'this is my secret key, there are many like it, but this one is mine'
              )