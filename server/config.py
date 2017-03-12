# -*- coding: utf-8 -*-
"""
server config file
"""
from os.path import abspath, dirname, join


config = dict(
              port = 5000,
              experiment_root_dir = join(dirname(abspath(__file__)), 'experiments'),
              debug = True,
              hostname = '0.0.0.0',
              )