# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import sqlite3
from ast import literal_eval
from collections import MutableMapping
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.embed import notebook_div,components
from bokeh.io import save
from os.path import basename, join, dirname, isfile
from os import stat, remove
from json import dumps
#import GraphPlugins

class datasource(object):
    '''
    parses an experiment file into an sql table,
    or set path to the correct database if this is a previously parsed experiment
    takes file path as a parameter
    '''
    experiment_file = ''
    machines = []
    columns = []
    dataframe = pd.DataFrame()
    filename = ''
    dirpath = ''
    sqlpath = ''
    
    def __init__(self,file_path):
        self.experiment_file = file_path
        self.filename = basename(file_path)
        self.dirpath = dirname(file_path)
        self.sqlpath = file_path+'.db'
        start_pos = 0
        #check if this is a new experiment file, if it is or there is an error it will reparse it
        try:
            if isfile(self.sqlpath):
                conn = sqlite3.connect(self.sqlpath)
                archived_size = long(conn.execute('select size from attributes').fetchone()[0])
                archived_timestamp = conn.execute('select timestamp from attributes').fetchone()[0]
                conn.close()
                current_size = stat(self.experiment_file).st_size
                current_timestamp = stat(self.experiment_file).st_mtime
                #print 'archived={} {} current={} {}'.format(archived_size,type(archived_size),current_size,type(current_size))
                if archived_size < current_size: #exoerimetn fle grew since last time we scanned it
                    start_pos = archived_size + 1
#                    print '-D- changed old file, seeking to {}'.format(start_pos)
                elif archived_size > current_size: #experiment file shrunk, this should never happen
                    raise Exception('test file shrunk!')
                elif archived_size == current_size and current_timestamp > archived_timestamp:
#                    print '-D- current_timestamp:{} archived_timestamp{}'.format(current_timestamp,archived_timestamp)
                    raise Exception('test file timestamp changed!')
                else: #nothing changed since lst scan
#                    print '-D- old, unchanged file'
                    self.getcol()
                    return
        except sqlite3.OperationalError as e:
            print e
            conn.close()
            remove(self.sqlpath)
        except Exception as e:
            print e
            remove(self.sqlpath)
        #parse experiment file and get column names
        self.analyze(start_pos)
        self.getcol()
                
            
        
    def getcol(self):
        '''returns the column names and the names of the vms (vm-1. vm-2 ...)'''
        conn = sqlite3.connect(self.sqlpath)
        self.columns = pd.read_sql_query("select * from columns", conn)['0'].tolist()
        self.machines = pd.read_sql_query("select * from machines", conn)['0'].tolist()
        conn.close()
        

    #flattens multilevel dicts
    def flatten(self,d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                items.extend(self.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
        
        
    def analyze(self, start_pos):
        #initializing a few things
        dictlist = []
        filesize = stat(self.experiment_file).st_size
        timestamp = stat(self.experiment_file).st_mtime
        #read the expeiment file and parse it into a list of dicts
        with open(self.experiment_file) as inp:
            inp.seek(start_pos)
            for line in inp:
                name,typ,time,dic = line.split('@')
                dic = literal_eval(dic)
                if len(dic) == 0:
                    next
                dic['name'] = name
                dic['type'] = typ
                dic['timestamp'] = float(time)
                dic = self.flatten(dic,sep=':')
                for entry in dic:
                    if type(dic[entry]) in [list, dict, tuple] and entry not in ['name', 'type']:
                        dic[entry] = dumps(dic[entry])
                    elif type(dic[entry]) == 'str':
                        del dic[entry]
                    #if entry == 'cache_alloc':
                        #print type(dic[entry])
                dictlist.append(dic)
        
        #turn data into a dataFrame and delete middle stage
        frame = pd.DataFrame(dictlist)
        del dictlist
        frame.sort_values('timestamp', inplace=True)
        conn = sqlite3.connect(self.sqlpath)
        try:
            self.columns = frame.columns.tolist()
            self.machines = frame['name'].unique().tolist()
            pd.DataFrame(frame.columns).to_sql('columns',conn,if_exists='replace',index= False)
            pd.DataFrame(frame['name'].unique()).to_sql('machines',conn,if_exists='replace',index= False)
            frame.to_sql('data',conn,if_exists='append',index= False)
            pd.DataFrame([{'size':filesize, 'timestamp':timestamp}]).to_sql('attributes',conn, if_exists='replace', index= False)
            conn.close()
        except Exception as e:
            print e
            #print self.columns[12]
            conn.close()
        #self.dataframe = frame
        
        
    def plot(self, x, y, machines):
        '''
        deprecated and no longer used.
        left behind in case its required as referance, will be removed in the final product
        '''
        if type(machines) == str or type(machines) == unicode: machines = [machines]
        print "-D- x:|{}| y:|{}| machines:|{}|".format(x,y,machines)
        print type(machines)
        #frame = self.dataframe
        #print frame
        figure_name = 'line'
        colors = ['blue', 'red', 'green', 'pink', 'orange']
        parameters = []
        for machine in machines:
            print "-D- machine:|{}|".format(machines)
            parameters.append({'machine':machine, 'x':x, 'y':y, 'color':colors.pop(0)}) # , 'color':'red'
        fig = figure(title=figure_name,sizing_mode='stretch_both', x_axis_label=x ,y_axis_label=y ,tools=['hover','crosshair','wheel_zoom','box_zoom','pan','save','resize','reset'])
        conn = sqlite3.connect(self.sqlpath)
        try:
            for params in parameters:
            #take only rows that contain these columns
                
                frame_slice = pd.read_sql_query("select `{x}`,`{y}`,`name` from data where `{x}` != '' and `{y}` != '' and `name` = '{machine}' order by `{x}` asc".format(**params), conn)
                #print frame_slice 
                #return
                #frame_slice = frame[frame[params['y']] > 0.0]
                #frame_slice = frame_slice[frame_slice[params['x']] > 0.0]
                #frame_slice = frame_slice[frame_slice.name == params['machine']][[params['x'], params['y']]]
                #print frame_slice
                fig.line(source=ColumnDataSource(frame_slice), x=params['x'],y=params['y'], line_width=2, legend=params['machine'], color=params['color'])
        except 'asd' as e:
            print e
            conn.close()
        conn.close()
        name = '{}_{}_{}'.format(self.filename,x,y)
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
        if __name__ == '__main__':
            show(fig)
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
    root_dir = 'Z:\\GIT\\REM\\server'
    exp_file = 'experiments\\exp1\\exp-plotter'
    path_to_file = join(root_dir,exp_file)
    print 'base={} dirname={}'.format(basename(path_to_file), dirname(path_to_file))
    data = datasource(join(root_dir,exp_file))
    data.plot('timestamp','performance',['vm-1'])
    #data.analyze()
    #print data.machines
    #print data.columns
    #print type(data.machines)
    #print data.plot('timestamp','performance','vm-1')
    
    
    
    