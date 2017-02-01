# -*- coding: utf-8 -*-
"""
guidline on how to create a graph plugin
"""

# -*- coding: utf-8 -*-


import pandas as pd
import sqlite3
from bokeh.embed import components
from os.path import join
from collections import OrderedDict
from bokeh.io import save

#usually you will use one and only one of the following
#never import things directly from charts or plotting (e.g. from bokeh.chart import ...) as it causes collisions!
from bokeh import charts
#from bokeh import plotting

class template(object):
    '''the name of the class must be the same name as the filename 
        it is case sensetive and it is what you will see in the graph selection in the webpage'''
    def getparameters(self):
        '''
        this function is used by the web page to query the user for data
        the order of the items in the dict are the order you will see them in the web page, so use OrderedDict for consitency
        each data item is a dict containing 2 things: type - the type of input(i.e. single item from a list(single), multiple items from a list(multiple) etc..)
            and source - the source of input (i.e cols for the names of data columns or name for the values of the name column)
        the return value should be a dict with a single key, the class name, and the value should be the dict of parameters to query the user for
        '''
        
        params = OrderedDict()
        params['x_axis'] = {'type':'single','source':'cols'}
        params['y_axis'] = {'type':'single','source':'cols'}
        params['group_by'] ={'type':'single','source':'name'}
        return {'template':params}
        #example of how it could look
        #return {'template': {'x-axis':'single', 'y-axis':'single', 'group-by':'multiple'}}
        
    def plot(self, filename, sqlpath, x_axis, y_axis, group_by):
        '''
        the plot fucntion will always recieve the following inputs:
            filename - the name of teh experiment file
            sqlpath - the path to the sqlite database of the experiment
            the requested parameters - the same as they were in the getparameters function
        the body of the functions hould create a graph using either of the plotting interfaced (charts/plotting)
        the return should be a dict {'div':div, 'js':js_path} 
        '''
        
        parameters = {'group_by':group_by, 'x':x_axis, 'y':y_axis}
        conn = sqlite3.connect(sqlpath)
        try:
                frame_slice = pd.read_sql_query("select `{x}`,`{y}` from data where `{x}` != '' and `{y}` != '' and `name` = '{group_by}' order by `{x}` asc".format(**parameters), conn)
                #frame_slice = pd.read_sql_query("select `timestamp`,`performance` from data where `timestamp` != '' and `performance` != '' and `name` = 'vm-1' order by `timestamp` asc", conn)

        except Exception as e:
            print e
            conn.close()
        conn.close()
        #graph generation
        fig = charts.Step(data=frame_slice, x=x_axis, y=y_axis)
        #fig = charts.Step(data=frame_slice, x='timestamp', y='performance', legend=True, tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        
        #if your graph object is named 'fig' you can copy the following code as is
        #omit the lines up to the next comment if you do not want to save the graph as an html to disk
        name = '{}_{}_{}_{}'.format(filename,self.getparameters().keys()[0],x_axis,y_axis)
        name = name.replace(':','')
        charts.output_file('static\\'+name+'.html', title=name, mode='cdn', root_dir=None)
        save(fig)
        #this is where the graph is broken into embeddable components
        js,div =components(fig, wrap_script = False, wrap_plot_info = True)
#        div_path = join('bokeh','{}_div.html'.format(name))
#        with open (join('static',div_path), 'w') as out:
#            out.write(div)
        #the js component must be saved to disk
        js_path = join('bokeh','{}_js.js'.format(name))
        with open (join('static', js_path), 'w') as out:
            out.write(js)
        return {'div':div, 'js':js_path}
        
    