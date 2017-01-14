# -*- coding: utf-8 -*-


import pandas as pd
#import numpy as np
import sqlite3
#from ast import literal_eval
#from collections import MutableMapping
from bokeh.embed import components
from os.path import join
#from json import dumps
from collections import OrderedDict
from bokeh.io import save
from bokeh import charts
#Step, show, output_file, ColumnDataSource

class step(object):
    def getparameters(self):
        #return {'Line': {'x-axis':'single', 'y-axis':'single', 'group-by':'multiple'}}
        params = OrderedDict()
        params['x_axis'] = {'type':'single','source':'cols'}
        params['y_axis'] = {'type':'single','source':'cols'}
        params['group_by'] ={'type':'single','source':'machines'}
        return {'step':params}
        
    def plot(self, filename, sqlpath, x_axis, y_axis, group_by):

        parameters = []
#        for machine in group_by:
#            print "-D- machine:|{}|".format(machine)
        parameters = {'group_by':group_by, 'x':x_axis, 'y':y_axis}
#            i+=1
#        fig = figure(title=figure_name,sizing_mode='stretch_both', x_axis_label=x_axis ,y_axis_label=y_axis ,tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        conn = sqlite3.connect(sqlpath)
        try:
            #for params in parameters:
            #take only rows that contain these columns
                
                #frame_slice = pd.read_sql_query("select `{x}`,`{y}` from data where `{x}` != '' and `{y}` != '' and `name` = '{group_by}' order by `{x}` asc".format(**parameters), conn)
                frame_slice = pd.read_sql_query("select `timestamp`,`performance` from data where `timestamp` != '' and `performance` != '' and `name` = 'vm-1' order by `timestamp` asc", conn)
                
                #print "select `{x}`,`{y}` from data where `{x}` != '' and `{y}` != '' and `name` = '{group_by}' order by `{x}` asc".format(**parameters)
                #print frame_slice 
                #return
                #frame_slice = frame[frame[params['y']] > 0.0]
                #frame_slice = frame_slice[frame_slice[params['x']] > 0.0]
                #frame_slice = frame_slice[frame_slice.name == params['machine']][[params['x'], params['y']]]
                #print frame_slice
                #fig.line(source=ColumnDataSource(frame_slice), x=params['x'],y=params['y'], line_width=2, legend=params['machine'], color=params['color'])
        except Exception as e:
            print e
            conn.close()
        conn.close()
        #frame_slice = pd.DataFrame(frame_slice)
        #print frame_slice
        #fig = charts.Step(data=frame_slice, x=x_axis, y=y_axis)
        fig = charts.Step(data=frame_slice, x='timestamp', y='performance')
        #fig = Bokehstep(frame_slice, x=x_axis, y=y_axis, legend=True, tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        name = '{}_{}_{}'.format(filename,x_axis,y_axis)
        name = name.replace(':','')
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
        charts.show(fig)
        return {'div':div, 'js':js_path}
        
if __name__ == '__main__':
    s = step()
    print s.plot('thing','z:\\GIT\\REM\\server\\experiments\\exp1\\exp-plotter.db','timestamp','performance','vm-1')
    
    
    
    