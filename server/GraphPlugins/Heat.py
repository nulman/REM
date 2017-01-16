# -*- coding: utf-8 -*-


import pandas as pd
#import numpy as np
import sqlite3
#from ast import literal_eval
#from collections import MutableMapping
from bokeh import charts
from bokeh.embed import components
from bokeh.io import save
from os.path import join
#from json import dumps
from bokeh.palettes import Set1_9 
from collections import OrderedDict

#the following is for proof of concept
from bokeh.sampledata.unemployment1948 import data
class Heat(object):
    def getparameters(self):
        #return {'Line': {'x-axis':'single', 'y-axis':'single', 'group-by':'multiple'}}
        params = OrderedDict()
        params['x_axis'] = {'type':'single','source':'cols'}
        params['y_axis'] = {'type':'single','source':'cols'}
        params['group_by'] ={'type':'multiple','source':'machines'}
        return {'Heat':params}
        
    def plot(self, filename, sqlpath, x_axis, y_axis, group_by):
        data['Year'] = data['Year'].astype(str)
        unempl = pd.melt(data, var_name='Month', value_name='Unemployment', id_vars=['Year'])
        fig = charts.HeatMap(unempl, x='Year', y='Month', values='Unemployment', stat=None, sort_dim={'x': False}, sizing_mode='stretch_both')
        name = '{}_{}_{}_{}'.format(filename,self.getparameters().keys()[0],x_axis,y_axis)
        name = name.replace(':','')
        unempl.to_json('static\\'+name+'.json')
        charts.output_file('static\\'+name+'.html', title=name, mode='cdn', root_dir=None)
        save(fig)
        js,div =components(fig, wrap_script = False, wrap_plot_info = True)
        div_path = join('bokeh','{}_div.html'.format(name))
        with open (join('static',div_path), 'w') as out:
            out.write(div)
        js_path = join('bokeh','{}_js.js'.format(name))
        with open (join('static', js_path), 'w') as out:
            out.write(js)
#        if __name__ == '__main__':
#            show(fig)
        return {'div':div, 'js':js_path}



