# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 13:12:27 2016

@author: anulman
"""

import pandas as pd
import numpy as np
from ast import literal_eval
from collections import MutableMapping
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.embed import notebook_div,components
from bokeh.io import save
from os.path import basename, join

class datasource(object):
    experiment_file = ''
    machines = []
    columns = []
    dataframe = pd.DataFrame()
    filename = ''
    
    def __init__(self,file_path):
        self.experiment_file = file_path
        self.filename = basename(file_path)

    #flattens dicts
    def flatten(self,d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                items.extend(self.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
        
        
    def analyze(self):
        #initializing a few things
        dictlist = []
        
        #read the expeiment file and parse it into a list of dicts
        with open(self.experiment_file) as inp:
            for line in inp:
                name,typ,time,dic = line.split('@')
                dic = literal_eval(dic)
                if len(dic) == 0:
                    next
                dic['name'] = name
                dic['type'] = typ
                dic['timestamp'] = float(time)
                dictlist.append(self.flatten(dic,sep=':'))
        
        #turn data into a dataFrame and delete middle stage
        frame = pd.DataFrame(dictlist)
        del dictlist
        
        frame.sort_values('timestamp', inplace=True)
        
        #display column names for selection
        self.columns = frame.columns.tolist()
        #display machines
        self.machines = frame['name'].unique().tolist()
        self.dataframe = frame
        
        
    def plot(self, x, y, machines):
        if type(machines) == str or type(machines) == unicode: machines = [machines]
        print "-D- x:|{}| y:|{}| machines:|{}|".format(x,y,machines)
        print type(machines)
        frame = self.dataframe
        #print frame
        figure_name = 'line'
        colors = ['blue', 'red', 'green', 'pink', 'orange']
        parameters = []
        for machine in machines:
            print "-D- machine:|{}|".format(machines)
            parameters.append({'machine':machine, 'x':x, 'y':y, 'color':colors.pop(0)}) # , 'color':'red'
        fig = figure(title=figure_name,sizing_mode='stretch_both', x_axis_label=x ,y_axis_label=y ,tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        for params in parameters:
        #take only rows that contain these columns
            frame_slice = frame[frame[params['y']] > 0.0]
            frame_slice = frame_slice[frame_slice[params['x']] > 0.0]
            frame_slice = frame_slice[frame_slice.name == params['machine']][[params['x'], params['y']]]
            print frame_slice
            fig.line(source=ColumnDataSource(frame_slice), x=params['x'],y=params['y'], line_width=2, legend=params['machine'], color=params['color'])
        name = '{}_{}_{}'.format(self.filename,x,y)
        output_file('static\\'+name+'.html', title=name, autosave=False, mode='cdn', root_dir=None)
        save(fig)
        js,div =components(fig, wrap_script = False, wrap_plot_info = True)
        div_path = join('bokeh','{}_div.html'.format(name))
        with open (join('static',div_path), 'w') as out:
            out.write(div)
        js_path = join('bokeh','{}_js.js'.format(name))
        with open (join('static', js_path), 'w') as out:
            out.write(js)
        #show(fig)
        return {'div':div, 'js':js_path}
'''        
    #set parameters for the lines
    figure_name = 'line'
    parameters = []
    parameters.append({'machine':'vm-1', 'x':'timestamp', 'y':'cache_and_buff', 'color':'red'})
    parameters.append({'machine':'vm-1', 'x':'timestamp', 'y':'mem_unused', 'color':'blue'})
    
    fig = figure(title=figure_name,tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
    for params in parameters:
        #take only rows that contain these columns
        frame_slice = frame[frame[params['y']] > 0.0]
        frame_slice = frame_slice[frame_slice[params['x']] > 0.0]
        frame_slice = frame_slice[frame_slice.name == params['machine']][[params['x'], params['y']]]
        fig.line(source=ColumnDataSource(frame_slice), x=params['x'],y=params['y'], line_width=4, legend=params['y'], color=params['color'])
    
    
    js,div =components(fig, wrap_script = True, wrap_plot_info = True)
'''
if __name__ == '__main__':
    root_dir = 'Z:\\REM\\server'
    exp_file = 'experiments\\exp1\\exp-plotter'
    data = datasource(join(root_dir,exp_file))
    data.analyze()
    #print data.machines
    #print data.columns
    #print type(data.machines)
    print data.plot('timestamp','performance','vm-1')
    
    
    
    