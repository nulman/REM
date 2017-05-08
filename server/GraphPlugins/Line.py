# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
'''

import pandas as pd
import sqlite3
from bokeh import plotting
from bokeh.embed import components
from bokeh.io import save
from os.path import join as join_path
from bokeh.palettes import Set1_9 
from collections import OrderedDict

class Steve(object):
    def getparameters(self):
        params = OrderedDict()
        params['x_axis'] = {'type':'single', 'filterByValue':False}
        params['y_axis'] = {'type':'single', 'filterByValue':False}
        params['group_by'] ={'type':'multiple', 'filterByValue':True}
        #__name__ is GraphPlugins.Line  we just want the word "Line"
        return {__name__[__name__.index('.')+1:]:params}
        
    def plot(self, filename, sqlpath, x_axis, y_axis, group_by):
        group_by, value = group_by.iteritems().next()
        if type(value) != list: value = [value]

        figure_name = 'line'
        colors = list(Set1_9)
        parameters = []
        i = 0
        for val in value:
            parameters.append({'col':group_by, 'value':val, 'x':x_axis, 'y':y_axis, 'color':colors[i%9]}) # , 'color':'red'
            i+=1
        fig = plotting.figure(title=figure_name,sizing_mode='stretch_both', x_axis_label=x_axis ,y_axis_label=y_axis ,tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        conn = sqlite3.connect(sqlpath)
        dump = pd.DataFrame()
        try:
            for params in parameters:
            #take only rows that contain these columns
                frame_slice = pd.read_sql_query("select `{x}`,`{y}`,`{col}` from data where `{x}` != '' and `{y}` != '' and `{col}` = '{value}' order by `{x}` asc".format(**params), conn)
                dump = dump.append(frame_slice)
                fig.line(source=plotting.ColumnDataSource(frame_slice), x=params['x'],y=params['y'], line_width=2, legend=params['col'], color=params['color'])
        finally:
            conn.close()
        conn.close()
        name = '{}_{}_{}_{}'.format(filename,self.getparameters().keys()[0],x_axis,y_axis)
        name = name.replace(':','')
        dump = dump.reset_index(drop=True)
        dump.to_json(join_path('exports', name+'.json'))
        del(dump)
        plotting.output_file(join_path('static', name+'.html'), title=name, mode='inline', root_dir=None)
        save(fig)
        js,div =components(fig, wrap_script = False, wrap_plot_info = True)
        return {'div':div, 'js':js}

        