# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
'''

import pandas as pd
#import numpy as np
import sqlite3
#from ast import literal_eval
#from collections import MutableMapping
from bokeh.embed import components
from os.path import join as join_path
#from json import dumps
from collections import OrderedDict
from bokeh.io import save
from bokeh import charts
#Step, show, output_file, ColumnDataSource

class Step(object):
    def getparameters(self):
        params = OrderedDict()
        params['x_axis'] = {'type':'single', 'filterByValue':False}
        params['y_axis'] = {'type':'single', 'filterByValue':False}
        params['group_by'] ={'type':'single', 'filterByValue':True}
        return {__name__[__name__.index('.')+1:]:params}
        
    def plot(self, filename, sqlpath, x_axis, y_axis, group_by):

        parameters = []
        group_by, value = group_by.iteritems().next()
        parameters = {'group_by':group_by, 'x':x_axis, 'y':y_axis, 'val':value}
        conn = sqlite3.connect(sqlpath)
        try:
            #for params in parameters:
            #take only rows that contain these columns
                query = "select `{x}`,`{y}` from data where `{x}` != '' and `{y}` != '' and `{group_by}` = '{val}' order by `{x}` asc".format(**parameters)
                frame_slice = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        fig = charts.Step(data=frame_slice, x='{}'.format(x_axis), y='{}'.format(y_axis))
        name = '{}_{}_{}_{}'.format(filename,self.getparameters().keys()[0],x_axis,y_axis)
        name = name.replace(':','')
        charts.output_file(join_path('static',name+'.html'), title=name, mode='cdn', root_dir=None)
        save(fig)
        js,div =components(fig, wrap_script = False, wrap_plot_info = True)
        return {'div':div, 'js':js}
        
    
    
    