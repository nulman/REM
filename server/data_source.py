# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
'''

import pandas as pd
import sqlite3
from ast import literal_eval
from collections import MutableMapping
from os.path import basename, dirname, isfile
from os import stat, remove
from json import dumps

class Datasource(object):
    '''
    parses an experiment file into an sql table,
    or set path to the correct database if this is a previously parsed experiment
    takes file path as a parameter
    '''

    
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
                if archived_size < current_size: #experiment fle grew since last time we scanned it
                    start_pos = archived_size + 1
                elif archived_size > current_size: #experiment file shrunk, this should never happen
                    raise Exception('test file shrunk!')
                elif archived_size == current_size and current_timestamp > archived_timestamp:
                    raise Exception('test file timestamp changed!')
                else: #nothing changed since lst scan
                    self.generate_cols()
                    return
        except Exception as e:
            print e
            remove(self.sqlpath)
        finally:
            if 'conn' in locals():
                conn.close()
        #parse experiment file and get column names
        self.analyze(start_pos)
        self.generate_cols()
                
            
        
    def generate_cols(self):
        '''generates the column names'''
        conn = sqlite3.connect(self.sqlpath)
        self.columns = pd.read_sql_query("select * from columns", conn)['0'].tolist()
        conn.close()
        
    def get_vals(self,col):
        '''returns the distinct values of a particular column'''
        conn = sqlite3.connect(self.sqlpath)
        result = pd.read_sql_query("select distinct([{}]) from data where [{}] != '' ".format(col,col), conn)[col].tolist()
        conn.close()
        return result

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
        '''analyzes the experiment file and creates an sql file with the data'''
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
                if len(dic.keys()) > 3:
                    dictlist.append(dic)
        
        #turn data into a dataFrame and delete middle stage
        frame = pd.DataFrame(dictlist)
        del dictlist
        frame.sort_values('timestamp', inplace=True)
        conn = sqlite3.connect(self.sqlpath)
        try:
            self.columns = frame.columns.tolist()
            pd.DataFrame(frame.columns).to_sql('columns',conn,if_exists='replace',index= False)
            frame.to_sql('data',conn,if_exists='append',index= False)
            pd.DataFrame([{'size':filesize, 'timestamp':timestamp}]).to_sql('attributes',conn, if_exists='replace', index= False)
            conn.close()
        except Exception as e:
            print e
        finally:
            conn.close()
        

    
    
    
    