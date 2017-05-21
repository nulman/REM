"""
@editor: Liran Funaro <funaro@cs.technion.ac.il>
@author: Alex Nulman <anulman@cs.haifa.ac.il>
"""

import os
import string
from contextlib import closing

import pandas as pd
import sqlite3
import  json

from ast import literal_eval
from collections import MutableMapping

class DataSource(object):
    """
    parses an experiment file into an sql table,
    or set path to the correct database if this is a previously parsed experiment
    takes file path as a parameter
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    def __init__(self, file_path, export_path="exports"):
        if not os.path.isfile(file_path):
            raise Exception("Data file not found")

        self.__data_file = file_path

        self.__dir_path, self.__file_name = os.path.split(file_path)
        self.__export_path = os.path.join(self.__dir_path, export_path)
        if not os.path.isdir(self.__export_path):
            os.makedirs(self.__export_path)

        self.__name, _ext = os.path.splitext(self.__file_name)
        self.__sql_file_path = os.path.join(self.__export_path, self.__name+'.db')

        self.__column_names = None
        start_pos = self.__new_data_read_position__()

        if start_pos is not None:
            self.analyze(start_pos)
        self.generate_cols()

    @property
    def column_names(self):
        return self.__column_names

    @property
    def file_name(self):
        return self.__file_name

    @property
    def path(self):
        return self.__dir_path

    @property
    def name(self):
        return self.__name

    def export_file_path(self, ext, *parameters):
        """ Create a valid file name for a plot export """
        file_name_list = [self.name]
        file_name_list.extend(parameters)
        file_name = '_'.join(file_name_list)
        file_name = "%s.%s" % (file_name, ext)
        file_name = ''.join(c for c in file_name if c in self.valid_chars)

        return os.path.join(self.__export_path, file_name)

    def db_connection(self):
        return closing(sqlite3.connect(self.__sql_file_path))

    def is_db_exits(self):
        return os.path.isfile(self.__sql_file_path)

    def __new_data_read_position__(self):
        """
        Check if the data file exists.
        If it is or there is an error it will re analyze it
        """
        if not self.is_db_exits():
            return 0

        try:
            with self.db_connection() as conn:
                archived_size = long(conn.execute('select size from attributes').fetchone()[0])
                archived_timestamp = conn.execute('select timestamp from attributes').fetchone()[0]

            data_file_stats = os.stat(self.__data_file)
            current_size = data_file_stats.st_size
            current_timestamp = data_file_stats.st_mtime

            if archived_size < current_size:  # experiment fle grew since last time we scanned it
                return archived_size + 1
            elif archived_size > current_size:  # experiment file shrunk, this should never happen
                raise Exception('Test file shrunk!')
            elif archived_size == current_size and current_timestamp > archived_timestamp:
                raise Exception('Test file timestamp changed!')
            else:  # nothing changed since last scan
                return None
        except Exception as e:
            print "[ERROR]", e
            os.remove(self.__sql_file_path)
            return 0
                
    def generate_cols(self):
        """ Generates the column names """
        with self.db_connection() as conn:
            self.__column_names = pd.read_sql_query("select * from columns", conn)['0'].tolist()

    def get_distinct_values(self, col):
        """ Returns the distinct values of a particular column """
        with self.db_connection() as conn:
            return pd.read_sql_query("select distinct([{}]) from data where [{}] != '' ".format(col,col), conn)[col].tolist()

    @classmethod
    def __flatten__(cls, d, parent_key='', join_template='%s_%s'):
        """
        Flattens multilevel dicts
        Take from: http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
        """
        items = []
        for k, v in d:
            new_key = join_template % (parent_key, k) if parent_key else k
            if isinstance(v, MutableMapping):
                items.extend(cls.__flatten__(v.items(), new_key, join_template))
            else:
                items.append((new_key, v))
        return items

    @classmethod
    def flatten(cls, d, sep='_'):
        """ Flattens multilevel dicts """
        return cls.__flatten__(d.items(), parent_key='', join_template="%s"+sep+"%s")

    @classmethod
    def normalize_data(cls, data):
        for entry, value in cls.flatten(data, sep=':'):
            value_type = type(value)
            if entry in ['name', 'type', 'timestamp'] or value_type == str:
                continue
            if value_type in [list, dict, tuple]:
                value = json.dumps(value)
            yield entry, value

    def analyze_line(self, line):
        name, typ, time, dic = line.split('@')
        dic = literal_eval(dic)
        if not dic:
            return None
        dic = dict(self.normalize_data(dic))
        if not dic:
            return None

        dic['name'] = name
        dic['type'] = typ
        dic['timestamp'] = float(time)
        return dic

    def analyze(self, start_pos):
        """
        Parse and analyzes the data file and creates an SQL db file with the data
        """

        # Read the data file and parse it into a list of dicts
        dictlist = []
        with open(self.__data_file) as inp:
            inp.seek(start_pos)
            for line in inp:
                res = self.analyze_line(line)
                if res:
                    dictlist.append(res)
        
        #turn data into a dataFrame and delete middle stage
        frame = pd.DataFrame(dictlist)
        frame.sort_values('timestamp', inplace=True)
        try:
            data_file_stats = os.stat(self.__data_file)

            with self.db_connection() as conn:
                pd.DataFrame(frame.columns).to_sql('columns',conn,if_exists='replace',index= False)
                frame.to_sql('data', conn, if_exists='append', index= False)

                attribute_data = pd.DataFrame(
                    [{'size': data_file_stats.st_size, 'timestamp': data_file_stats.st_mtime}])
                attribute_data.to_sql('attributes', conn, if_exists='replace', index=False)
        except Exception as e:
            print "[ERROR]", e



    
    
    
    