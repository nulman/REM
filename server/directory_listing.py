# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
'''

from os import listdir, walk, environ, sep
from os.path import join as join_path, basename
from json import dumps
root_dir = environ['experiment_root_dir']
root_name = basename(root_dir)

def get_subtree(current_path = []):
    '''
    generates file/folder subtrees for the file walker
    '''
    json_string = []
    if current_path == [] or current_path == '':
        path_to_list = root_dir
    else:
        if sep == '/': #add initial / in unix based systems
            current_path.insert(0, sep)
        path_to_list = join_path(*current_path)
    for _,dirs,files in walk(path_to_list):
        for d in dirs:
            item = {}
            item['text'] = d
            item['children'] = True if listdir(join_path(path_to_list,d)) else False
            item['id'] = join_path(path_to_list, d)
            item['icon'] = 'glyphicon glyphicon-folder-open'
            item['type'] = 'default'
            item['state'] = {'opened':False}
            json_string.append(item)
        for f in files:
            try:
                if str(f).endswith('.db'):
                    continue
            except UnicodeEncodeError as e:
                print e
                continue
            item = {}
            item['text'] = f
            item['children'] = False
            item['icon'] = 'glyphicon glyphicon-file'
            item['id'] = join_path(path_to_list, f)
            item['type'] = 'file'
            json_string.append(item)
        break #we only want one layer of listing
    json_string = {'json':json_string, 'url':root_dir}
    return dumps(json_string)

if __name__ == '__main__':            
    print get_subtree()