# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 12:34:23 2016

@author: anulman
"""

import os
import sqlite3
from sys import argv
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app, Response
from json import dumps
from os.path import abspath, dirname
from datasource import datasource
#from BeautifulSoup import BeautifulStoneSoup
if(len(argv) > 1):
    os.chdir(argv[1])

app = Flask(__name__)
app.config.from_object(__name__)
os.environ['experiment_root_dir'] = os.path.join(dirname(abspath(__file__)), 'experiments')
root_dir = os.environ['experiment_root_dir']
print os.environ['experiment_root_dir']
data = ''
#current_app.config[ ('root_dir', dirname(abspath(__file__)))
   
from DirectoryListing import getSubtree

@app.route('/',methods=['GET', 'POST'])
def main_page():
    #x = [1,2,3,'steve',{'a':34, 'b':17},4]
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
        res = {'cols':data.columns, 'machines':data.machines}
    return Response(dumps(res), mimetype='application/json')

@app.route('/plot',methods=['GET'])
def plot():
    global data
    if type(data) == str: return ''
    print "-D- {} {}".format(request.method, type(request.method))
    print request.query_string
    x = request.args.get('x').replace('#','')
    y = request.args.get('y').replace('#','')
    machines = request.args.get('machines').replace('#','')
    print "-D- x:{} y:{} machines:{}".format(x,y,machines)
    components = data.plot(x,y,machines)
    print '-D- data.machines:{}'.format(data.machines)
    print components
    return Response(dumps(components), mimetype='application/json')
try:
    if __name__ == '__main__':
        app.run(host= '0.0.0.0', threaded=True)
except KeyboardInterrupt:
    print 'alas poor yorrick..'
    exit
    