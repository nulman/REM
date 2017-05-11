'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
server config file
'''
import os

# data_dir is the initial directory to start the file browser in
# it will default to the server location.
data_root_dir = os.path.dirname(os.path.abspath(__file__))

example_data_dir = os.path.join(data_root_dir, '../example-data')
if example_data_dir:
    data_root_dir = example_data_dir

config = dict(
              port = 5000,
              experiment_root_dir = os.path.normpath(os.path.expanduser(data_root_dir)),
              debug = True,
              hostname = '0.0.0.0',
              #the SECRET_KEY is required, without it you cant have sessions.
              SECRET_KEY = 'this is my secret key, there are many like it, but this one is mine'
              )