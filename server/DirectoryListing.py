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
    if current_path == '':
        path_to_list = root_dir
    else:
        path_to_list = current_path
    #print '-D- ' + path_to_list
    '''if current_path == root_dir:
        json_string = [{'text':root_name ,'children':json_string, 
                               'id':path_to_list,'icon':'glyphicon glyphicon-folder-open','type':'default','state':{'opened':False}}]
    else:'''
    for _,dirs,files in walk(path_to_list):
        #print 'dirs:'
        for d in dirs:
            #print d
            item = {}
            item['text'] = d
            item['children'] = True if listdir(join(path_to_list,d)) else False
            item['id'] = join(path_to_list, d)
            item['icon'] = 'glyphicon glyphicon-folder-open'
            item['type'] = 'default'
            item['state'] = {'opened':False}
            json_string.append(item)
        #print 'files:'
        for f in files:
            try:
                if str(f).endswith('.db'):
                    continue
            except UnicodeEncodeError as e:
                print e
                continue
            #print f
            item = {}
            item['text'] = f
            item['children'] = False
            item['icon'] = 'glyphicon glyphicon-file'
            item['id'] = join(path_to_list, f)
            item['type'] = 'file'
            json_string.append(item)
        break #we only want one layer of listing
    #json_string = [json_string]
    json_string = {'json':json_string, 'url':root_dir}
    return dumps(json_string)

if __name__ == '__main__':            
    print getSubtree()