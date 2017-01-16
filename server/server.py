# -*- coding: utf-8 -*-
"""
@author: anulman

this script takes exactly one (optional) parameter the FULL path to the experiments folder
"""

import os
from sys import argv
#if(len(argv) > 1):
#    print argv
#    os.chdir(argv[1])
#import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app, Response
from json import dumps, loads
from os.path import abspath, dirname
import socket
#from BeautifulSoup import BeautifulStoneSoup
app = Flask(__name__)
app.config.from_object(__name__)

#app.config.update(dict(
#    SECRET_KEY='this is my secret key, there are many like it, but this one is mine',
#    USERNAME='admin',
#    PASSWORD='iddqd'
#))
#print '__file__ : {}'.format(__file__)
#print 'dirname(abspath(__file__)) : {}'.format(dirname(abspath(__file__)))
if(len(argv) > 1):
    os.environ['experiment_root_dir'] = argv[1]
    root_dir = os.environ['experiment_root_dir']
else:
    os.environ['experiment_root_dir'] = os.path.join(dirname(abspath(__file__)), 'experiments')
    root_dir = os.environ['experiment_root_dir']
#print os.environ['experiment_root_dir']

from datasource import datasource
from DirectoryListing import getSubtree
import GraphPlugins

data = ''
#current_app.config[ ('root_dir', dirname(abspath(__file__)))

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
    #return url_for('static', filename='index.html')
    #return dumps(x)
    return redirect(os.path.join('static', 'index.html'))
    
@app.route('/listdir',methods=['GET'])
def listdir():
    res = ''
    if request.method == 'POST':
        print request.form
    else:
        '''print "-D- {} {}".format(request.method, type(request.method))
        print request.query_string
        print "-D- id: {}".format(request.args.get('id'))'''
        requested_path = request.args.get('id')
        if requested_path == None:
            requested_path = ''
        print "-D- requested_path: {}".format(requested_path)
        requested_path = requested_path.replace('#','')
        #if requested_path and requested_path != '#' : requested_path = BeautifulStoneSoup(requested_path, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).encode("UTF-8")
        #print "-D- id: {}".format(requested_path)
        res = getSubtree(requested_path)
        #print res
        #print res
    return Response(res, mimetype='application/json')
    #return Response('[{"text":"root","children":[{"text":"DefaultJSONStructures","children":true,"id":"DefaultJSONStructures","icon":"folder"},{"text":"University01","children":true,"id":"University01","icon":"folder"},{"text":"University02","children":true,"id":"University02","icon":"folder"},{"text":"University03","children":true,"id":"University03","icon":"folder"}],"id":"\/","icon":"folder","state":{"opened":true,"disabled":true}}]', mimetype='application/json')


@app.route('/getcolumns',methods=['GET'])
def listcols():
    print '-D- in get cols'
    #x = [1,2,3,'steve',{'a':34, 'b':17},4]
    res = ''
    global data
    if request.method == 'POST':
        print request.form
    else:
        print "-D- {} {}".format(request.method, type(request.method))
        print request.query_string
        print "-D- experiment: {}".format(request.args.get('experiment'))
        requested_path = request.args.get('experiment')
        print "-D- experiment: {}".format(requested_path)
        requested_path = requested_path.replace('#','')
        #if requested_path and requested_path != '#' : requested_path = BeautifulStoneSoup(requested_path, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).encode("UTF-8")
        print "-D- experiment: {}".format(requested_path)
        data = datasource(requested_path)
        #data.analyze()
        data.getcol()
        res = {'cols':data.columns, 'machines':data.machines, 'models':GraphPlugins.graphtypes}
    return Response(dumps(res), mimetype='application/json')



@app.route('/plot',methods=['POST'])
def plot():
    global data
    #if type(data) == str: return ''
    #print "-D- {} {}".format(request.method, type(request.method))
    #print request.data
    parameters = request.get_json(force=True)
    #print parameters
    #type(parameters)
    #parameters = loads(parameters)
    graphtype = parameters.keys()[0]
    #print request.query_string
    #x = request.args.get('x').replace('#','')
    #y = request.args.get('y').replace('#','')
    #machines = request.args.get('machines').replace('#','')
    #print "-D- x:{} y:{} machines:{}".format(x,y,machines)
    #components = data.plot(x,y,machines)
    graph = getattr(getattr(GraphPlugins,graphtype),graphtype)() #this will create an instance of the requested graph type
    #graph = GraphPlugins.Line.Line()
    components = graph.plot(data.filename, data.sqlpath, **parameters[graphtype])
    #print '-D- data.machines:{}'.format(data.machines)
    #print components
    return Response(dumps(components), mimetype='application/json')
try:
    if __name__ == '__main__':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('',0))
        port = sock.getsockname()[1]
        port = 5000 #while developing use a static port
        print "-I- starting server on port {}".format(port)
        sock.close()
        app.run(host = '0.0.0.0', port = port, threaded=True)
except KeyboardInterrupt:
    print 'alas poor yorrick..'
    exit
