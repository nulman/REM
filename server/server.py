# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>

this is teh main app, it takes no parameters, instead update config.py
'''

import os
from sys import modules
import sqlite3
from re import split
from flask import Flask, request, session, redirect,  abort, Response, current_app
from json import dumps, loads
from os.path import abspath, dirname, join as join_path
import pandas as pd
from config import config
import GraphPlugins
from path import path
import utilities
import traceback
from time import time

app = Flask(__name__)
app.last_touched = 0.0
app.config.from_object(__name__)
#apply config file settings
app.config.update(config)
if app.config.has_key('experiment_root_dir'):
    os.environ['experiment_root_dir'] = app.config['experiment_root_dir']
else:
    os.environ['experiment_root_dir'] = dirname(abspath(__file__))
from data_source import Datasource
from directory_listing import get_subtree


@app.route('/',methods=['GET'])
def main_page():
    return redirect(join_path('static', 'index.html'))
    
@app.route('/listdir',methods=['POST'])
def list_dir():
    '''
    generates subtrees for the file browser
    '''
    requested_path = request.get_json(force=True)
    if requested_path != []:
        requested_path = split(r'[\\\/]+', requested_path)
        #windows compatability
        if requested_path[0].endswith(':'):
            requested_path.insert(1,os.sep)
    res = get_subtree(requested_path)
    return Response(res, mimetype='application/json')


@app.route('/getcolumns',methods=['POST'])
def list_cols():
    '''
    initialized the experiment data object and parses the experiment file if required
    returns the column names in the experiment and the graph plugins
    '''
    module_reloader()
    requested_path = request.get_json(force=True)
    print requested_path
    try:
        session['requested_path'] = requested_path
        data = Datasource(requested_path)
    except SyntaxError as e:
        abort(500, description="malformed experiment file\n"+str(e))
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print traceback.format_exc()
        abort(500, description=message)
    res = {'cols':data.columns, 'models':GraphPlugins.graphtypes}
    return Response(dumps(res), mimetype='application/json')
    
@app.route('/getvals',methods=['POST'])
def get_values():
    '''
    returns all the distinct values of a data column
    '''
    column = request.get_json(force=True)
    if type(column) != dict or len(column) != 2:
        abort(500, description="bad request. please pass a single value dict\n")
    try:
        data = Datasource(session['requested_path'])
        column['parameters'] = data.get_vals(column['parameters'])
        return Response(dumps(column), mimetype='application/json')
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print traceback.format_exc()
        abort(500, description=message)

@app.route('/load',methods=['POST'])
def load_preset():
    '''
    returns presets depending on the requested value:
    ["all"] - will return all presets in the database
    [] - will return presets that can apply to the selected experiment file
    '''
    res = {}
    columns = request.get_json(force=True)
    conn = sqlite3.connect('internals.DB')
    frame = pd.read_sql_query('select * from presets order by name', conn)
    conn.close()
    if type(columns) == list and len(columns) == 1 and columns[0] == 'all':
        for index, row in frame.iterrows():
            res[row['name']] = loads(row['json'])
    else:
        if 'requested_path' not in session:
            abort(403, description="no experiment selected. please select an experiment from the file browser and click ok")
        data = Datasource(session['requested_path'])
        sieve = {x:1 for x in data.columns}
        for index, row in frame.iterrows():
            i = 0
            items = row['items'].split(',')
            for item in items:
                if sieve.has_key(item):
                    i+=1
                else:
                    break
            if i == len(items):
                res[row['name']] = loads(row['json'])
    return Response(dumps(res), mimetype='application/json')

    
@app.route('/save',methods=['POST'])
def save_preset():
    '''
    recieves a {'name':name, "preset": preset} dict
    where name is an arbitrary name for the preset (will overwrite presets with he same name)
    and preset is the the same as a graphplugin.getparameters
    example:
    {"name":"thing2","preset":{"Line":{"x_axis":"timestamp","y_axis":"performance","group_by":{"name":["vm-1","vm-2"]}}}}
    '''
    parameters = request.get_json()
    if type(parameters) != dict:
        abort(403, description="i was expecting a dict and instead i got a"+type(parameters))
    items = []
    name = parameters['name']
    preset = parameters['preset']
    gtype = preset.keys()[0]
    for key in preset[gtype].keys():
        ditem = GraphPlugins.graphtypes[gtype][key]
        if ditem['filterByValue']: #turns values back into column names (such as vm-1 => name)
            items.append(preset[gtype][key].keys()[0])
        elif type(preset[gtype][key]) == list:
            for sub_item in preset[gtype][key]:
                items.append(sub_item)
        else:
            items.append(preset[gtype][key])
    frame = []
    frame.append({})
    frame[0]['name'] = name
    frame[0]['json'] = dumps(preset)
    frame[0]['items'] = ','.join(items)
    frame = pd.DataFrame(frame)
    try:
        conn = sqlite3.connect('internals.DB')
        conn.execute('delete from presets where name = ?', [name])
        conn.commit()
        frame.to_sql('presets', conn, index=False,if_exists='append')
        conn.close()
    except Exception as e:
        print e
        conn.close()
    return Response(dumps(['Preset saved.']), mimetype='application/json')

@app.route('/delete',methods=['POST'])
def delete_preset():
    '''
    takes a list of names and deletes the associated presets if any
    example:
    ["name1","name2"]
    '''
    parameters = request.get_json()
    if type(parameters) != list or len(parameters) == 0:
        abort(403, description="i was expecting a non-empty list")
    try:
        conn = sqlite3.connect('internals.db')
        for name in parameters:
            conn.execute('delete from presets where name = ?', [name])
        conn.commit()
        conn.close()
    except Exception as e:
        print e
        conn.close()
    return Response(dumps(['Preset deleted.']), mimetype='application/json')

@app.route('/plot',methods=['POST'])
def plot():
    module_reloader()
    data = Datasource(session['requested_path'])
    if not hasattr(data, 'columns') or len(data.columns) == 0:
        abort(403, description="no experiment selected. please select and experiment from the file browser and click ok")
    parameters = request.get_json(force=True)
    graphtype = parameters.keys()[0]
    #this will create an instance of the requested graph type
    graph = getattr(getattr(GraphPlugins,graphtype),GraphPlugins.module_to_class[graphtype])()
    try:
        components = graph.plot(data.filename, data.sqlpath, **parameters[graphtype])
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        abort(400, description=message)
    return Response(dumps(components), mimetype='application/json')
    
    
def module_reloader():
    ''' this checks if the 'last_touched' in the app context was changed
        during this session and reloads the plugins in this thread if it was
    '''
    if 'last_reload' not in session:
        session['last_reload'] = 0.0
    with app.app_context():
        mtime = current_app.last_touched
    if mtime != session['last_reload']:
        session['last_reload'] = mtime
        reload(GraphPlugins)
    return
        
    
@app.route('/reloadplugin',methods=['GET', 'POST'])
def reload_plugin():
    '''reloads the plugins and updates 'last_touched' in the app context'''
    with app.app_context():
        current_app.last_touched = time()
    for item in os.listdir(os.path.dirname(GraphPlugins.__file__)):
        if str(item).endswith('.pyc'):
            os.remove( join_path(dirname(GraphPlugins.__file__),item))
    for item in [x for x in modules.keys() if x.startswith("GraphPlugins.")]:
        del modules[item]
    reload(GraphPlugins)
    return Response('Done')
    
        
###########################main###########################
try:
    if __name__ == '__main__':
        utilities.internals_checker()
        print "-I- starting server on port {}".format(app.config['port'])
        app.run(app.config['hostname'], port = app.config['port'], threaded=True)
except KeyboardInterrupt:
    print 'alas poor yorrick..'
    exit
