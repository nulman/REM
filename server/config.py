# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
server config file
'''
from os.path import abspath, dirname, join as join_path


config = dict(
              port = 5000,
              experiment_root_dir = join_path(dirname(abspath(__file__)), 'experiments'),
              debug = True,
              hostname = '0.0.0.0',
              )