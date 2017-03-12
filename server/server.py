# -*- coding: utf-8 -*-
"""
@author: anulman

this script takes exactly one (optional) parameter the FULL path to the experiments folder
"""

import os
from sys import modules, argv
#if(len(argv) > 1):
#    print argv
#    os.chdir(argv[1])
import sqlite3
from re import split
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app, Response
from json import dumps, loads
from os.path import abspath, dirname, join, realpath
import pandas as pd
from config import config
import GraphPlugins
from path import path

app = Flask(__name__)
app.config.from_object(__name__)
os.chdir(dirname(realpath(__file__)))

#app.config.update(dict(
#    SECRET_KEY='this is my secret key, there are many like it, but this one is mine',
#    USERNAME='admin',
#    PASSWORD='iddqd'
#))
#apply config file settings
app.config.update(config)
if app.config.has_key('experiment_root_dir'):
    os.environ['experiment_root_dir'] = app.config['experiment_root_dir']
else:
    os.environ['experiment_root_dir'] = join(dirname(abspath(__file__)), 'experiments')
from datasource import datasource
from DirectoryListing import getSubtree

data = ''
last_reload = 0.0

#@app.route('/test',methods=['GET', 'POST'])
#def login():
#    session['logged_in'] = True
#    flash('You were logged in')
#    return redirect(os.path.join('static', 'index.html'))

@app.route('/',methods=['GET', 'POST'])
def main_page():
    print session
#    if not session.get('logged_in'):
#        abort(401)
    if request.method == 'POST':
        print request.form
    else:
        print "{} {}".format(request.method, type(request.method))
    return redirect(os.path.join('static', 'index.html'))
    
@app.route('/listdir',methods=['POST'])
def listdir():
    '''
    generates subtrees for the file browser
    '''
    
##    requested_path = request.args.get('id')
##    if requested_path == None:
##        requested_path = []
    requested_path = request.get_json(force=True)
    if requested_path != []:
        requested_path = split(r'[\\\/]+', requested_path)
        #windows compatability
        if requested_path[0].endswith(':'):
            requested_path.insert(1,os.sep)
    #print "-D- requested_path: {}".format(requested_path)
##    requested_path = requested_path.replace('#','')
    #print "-D- id: {}".format(requested_path)
    res = getSubtree(requested_path)
    return Response(res, mimetype='application/json')

@app.route('/reloadplugin',methods=['GET', 'POST'])
def reloadplugin():
    '''reloads the plugins'''
    path(os.path.join(os.path.dirname(__file__), 'reloader')).touch()
    #os.remove(os.path.abspath(GraphPlugins.__file__))
    for item in os.listdir(os.path.dirname(GraphPlugins.__file__)):
        if str(item).endswith('.pyc'):
            os.remove( os.path.join(os.path.dirname(GraphPlugins.__file__),item))
    for item in [x for x in modules.keys() if x.startswith("GraphPlugins.")]:
        del modules[item]
    reload(GraphPlugins)
    return Response('Done')


@app.route('/getcolumns',methods=['GET'])
def listcols():
    '''
    initialized the experiment data object and parses the experiment file if required
    returns the column names in the experiment and the graph plugins
    '''
    
    module_reloader()
    #print '-D- in get cols'
    global data
#    print "-D- {} {}".format(request.method, type(request.method))
#    print request.query_string
#    print "-D- experiment: {}".format(request.args.get('experiment'))
    requested_path = request.args.get('experiment')
#    print "-D- experiment: {}".format(requested_path)
    requested_path = requested_path.replace('#','')
#    print "-D- experiment: {}".format(requested_path)
    try:
        data = datasource(requested_path)
    except SyntaxError as e:
        abort(500, description="malformed experiment file\n"+str(e))
    #data.getcol()
    res = {'cols':data.columns, 'name':data.machines, 'models':GraphPlugins.graphtypes}
    return Response(dumps(res), mimetype='application/json')

@app.route('/load',methods=['POST'])
def loadpreset():
    """
    returns presets depending on the requested value:
    ["all"] - will return all presets in the database
    [] - will return presets that can apply to the selected experiment file
    """
    res = {}
    columns = request.get_json(force=True)
    conn = sqlite3.connect('internals.DB')
    frame = pd.read_sql_query('select * from presets order by name', conn)
    conn.close()
    if type(columns) == list and len(columns) == 1 and columns[0] == 'all':
        for index, row in frame.iterrows():
            res[row['name']] = loads(row['json'])
    else:
        global data
        if type(data) == str:
            abort(403, description="no experiment selected. please select and experiment from the file browser and click ok")
        sieve = {x:1 for x in data.columns}
        for index, row in frame.iterrows():
            i = 0
            items = row['items'].split(',')
            #print 'items: ',items
            for item in items:
                if sieve.has_key(item):
                    i+=1
                else:
                    #print 'no such key ', item
                    break
            if i == len(items):
                res[row['name']] = loads(row['json'])
    return Response(dumps(res), mimetype='application/json')

    
@app.route('/save',methods=['POST'])
def savepreset():
    """
    recieves a {'name':name, "preset": preset} dict
    where name is an arbitrary name for the preset (will overwrite presets with he same name)
    and preset is the the same as a graphplugin.getparameters
    example:
    {"name":"thing2","preset":{"Line":{"x_axis":"timestamp","y_axis":"performance","group_by":["vm-1","vm-2"]}}}
    """
    parameters = request.get_json()
    if type(parameters) != dict:
        abort(403, description="i was expecting a dict and instead i got a"+type(parameters))
    items = []
#    print parameters
    name = parameters['name']
    preset = parameters['preset']
#    print preset
#    print type(preset)
    gtype = preset.keys()[0]
    for key in preset[gtype].keys():
        ditem = GraphPlugins.graphtypes[gtype][key]
        if ditem['source'] != 'cols': #turns values back into column names (such as vm-1 => name)
            items.append(ditem['source'])
        elif type(preset[gtype][key]) == list:
            for sub_item in preset[gtype][key]:
                items.append(sub_item)
        else:
            items.append(preset[gtype][key])
#    print 'name:{}\npreset:{}\nitems:{}'.format(name,preset,items)
    frame = pd.DataFrame([{'name':name, 'json':dumps(preset), 'items':','.join(items)}])
    try:
        conn = sqlite3.connect('internals.db')
        conn.execute('delete from presets where name = ?', [name])
        conn.commit()
        #print frame
        frame.to_sql('presets', conn, index=False,if_exists='append')
        conn.close()
    except Exception as e:
        print e
        conn.close()
    return Response(dumps(['Preset saved.']), mimetype='application/json')

@app.route('/delete',methods=['POST'])
def deletepreset():
    """
    takes a list of names and deletes the associated presets if any
    example:
    ["name1","name2"]
    """
    parameters = request.get_json()
#    print request
#    print parameters
#    print type(parameters)
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
    global data
    if not hasattr(data, 'columns') or len(data.columns) == 0:
        abort(403, description="no experiment selected. please select and experiment from the file browser and click ok")
    parameters = request.get_json(force=True)
    graphtype = parameters.keys()[0]
    graph = getattr(getattr(GraphPlugins,graphtype),graphtype)() #this will create an instance of the requested graph type
    components = graph.plot(data.filename, data.sqlpath, **parameters[graphtype])
    return Response(dumps(components), mimetype='application/json')
    
    
def module_reloader():
    """since this application is threaded each thread needs to reload the plugins individually
    this is achieved by "touching" a file and any thread that hasnt reloaded the module
    will see that its saved timestamp is different from the file and will reload the module
    and update its internal timestamp to match the file
    """
    global last_reload
    last_reload_tester = os.path.join(os.path.dirname(__file__), 'reloader')
    mtime = os.stat(last_reload_tester).st_mtime
    if mtime != last_reload:
        print "reloading! mtime was {} and is now {}".format(str(last_reload), str(mtime))
        print "type: {}".format(type(mtime))
        last_reload = mtime
        reload(GraphPlugins)
    return
        
        
###########################main###########################
try:
    if __name__ == '__main__':
#        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        sock.bind(('',0))
#        port = sock.getsockname()[1]
#        port = 5000 #while developing use a static port
        print "-I- starting server on port {}".format(app.config['port'])
#        sock.close()
        app.run(host = '0.0.0.0', port = app.config['port'], threaded=True)
except KeyboardInterrupt:
    print 'alas poor yorrick..'
    exit
