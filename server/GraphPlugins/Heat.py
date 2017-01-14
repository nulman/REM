# -*- coding: utf-8 -*-


import pandas as pd
#import numpy as np
import sqlite3
#from ast import literal_eval
#from collections import MutableMapping
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.embed import components
from bokeh.io import save
from os.path import join
#from json import dumps
from bokeh.palettes import Set1_9 
from collections import OrderedDict

class Heat(object):
    def getparameters(self):
        #return {'Line': {'x-axis':'single', 'y-axis':'single', 'group-by':'multiple'}}
        params = OrderedDict()
        params['x_axis'] = {'type':'single','source':'cols'}
        params['y_axis'] = {'type':'single','source':'cols'}
        params['group_by'] ={'type':'multiple','source':'machines'}
        return {'Heat':params}
        
    def plot(self, filename, sqlpath, x_axis, y_axis, group_by):
        if type(group_by) == str or type(group_by) == unicode: group_by = [group_by]
        print "-D- x_axis:|{}| y_axis:|{}| machines:|{}|".format(x_axis,y_axis,group_by)
        print type(group_by)
        #frame = self.dataframe
        #print frame
        figure_name = 'line'
        colors = list(Set1_9)
        parameters = []
        i = 0
        for machine in group_by:
            print "-D- machine:|{}|".format(machine)
            parameters.append({'machine':machine, 'x':x_axis, 'y':y_axis, 'color':colors[i%9]}) # , 'color':'red'
            i+=1
        fig = figure(title=figure_name,sizing_mode='stretch_both', x_axis_label=x_axis ,y_axis_label=y_axis ,tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        conn = sqlite3.connect(sqlpath)
        try:
            for params in parameters:
            #take only rows that contain these columns
                frame_slice = pd.read_sql_query("select * from data where name = 'vm-1' and `cache-bid` != 0",conn)
                frame_slice = pd.read_sql_query("select `{x}`,`{y}`,`name` from data where `{x}` != '' and `{y}` != '' and `name` = '{machine}' order by `{x}` asc".format(**params), conn)
                #print frame_slice 
                #return
                #frame_slice = frame[frame[params['y']] > 0.0]
                #frame_slice = frame_slice[frame_slice[params['x']] > 0.0]
                #frame_slice = frame_slice[frame_slice.name == params['machine']][[params['x'], params['y']]]
                #print frame_slice
                fig.line(source=ColumnDataSource(frame_slice), x=params['x'],y=params['y'], line_width=2, legend=params['machine'], color=params['color'])
        except Exception as e:
            print e
            conn.close()
        conn.close()
        name = '{}_{}_{}'.format(filename,x_axis,y_axis)
        name = name.replace(':','')
        output_file('static\\'+name+'.html', title=name, autosave=False, mode='cdn', root_dir=None)
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



