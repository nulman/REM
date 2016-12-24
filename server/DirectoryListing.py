# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from os import listdir, walk, environ
from os.path import isfile, join, isdir, abspath, dirname, basename
from os import chdir
from json import dumps
from flask import Flask, app
#chdir('Z:\\REM\\server')
root_dir = environ['experiment_root_dir']
#root_dir = dirname(abspath(__file__))
root_name = basename(root_dir)

def getSubtree(current_path = ''):
    json_string = []
    path_to_list = join (root_dir, current_path)
    #print '-D- ' + path_to_list
    for _,dirs,files in walk(path_to_list):
        #print 'dirs:'
        for d in dirs:
            #print d
            item = {}
            item['text'] = d
            item['children'] = True if listdir(join(root_dir,current_path,d)) else False
            item['id'] = join(current_path, d)
            item['icon'] = 'folder'
            json_string.append(item)
        #print 'files:'
        for f in files:
            #print f
            item = {}
            item['text'] = f
            item['children'] = False
            item['id'] = join(current_path, f)
            item['type'] = 'file'
            json_string.append(item)
        break #we only want one layer of listing
    if current_path == '':
        json_string = [{'text':root_name ,'children':json_string, 'id':'','icon':'folder','state':{'opened':False,'disabled':True}}]
    return dumps(json_string)

if __name__ == '__main__':            
    print getSubtree()