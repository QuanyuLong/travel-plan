#!/usr/bin/env python
#encoding: utf-8
#file: searchtrip.py

INDEX_DIR = "IndexFiles.index"

import sys, os, jieba, math, re
from eicreader import Reader
from initVM import *

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""

def parseCommand(command):
    '''
    input: C
    output: 
    '''
    allowed_opt =[]
    command_dict = {}
    opt = 'location'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = command_dict.get(opt, '') + ' ' + value
        else:
            command_dict[opt] = command_dict.get(opt, '') + ' ' + ' '.join(jieba.cut(i))
    return command_dict   

def run():
    while True:
        print
        print "Hit enter with no input to quit."
        command = unicode(raw_input("Query:"), 'utf-8')
        if command == '':
            return

        print
        print "Searching for:", command
        
        ans = search_trip(command)
        if ans != 'Interior Error':
            print "-------------------------------"
            for i in ans:
                print i, '|', ans.get(i, '')
            print

def search_trip(command):
    '''command must be encoded in unicode'''
    STORE_DIR = "index_trip"
    vm_env.attachCurrentThread()
    directory = SimpleFSDirectory(File(STORE_DIR))
    
    folders = {'parsed_ctrip':['source', 'location', 'introduction', 'score', 'img_list'],
                'parsed_qunar':['location', 'rank', 'score', 'time', 'introduction', 'img_list'],
                'eic_mfw':['location', 'introduction', 'img_list']}
    readers = constructReaders(folders)
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    
    command_dict = parseCommand(command)
    querys = BooleanQuery()
    for k,v in command_dict.iteritems():
        query = QueryParser(Version.LUCENE_CURRENT, k,
                            analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST)
    scoreDocs = searcher.search(querys, 50).scoreDocs
    print 'total: %s' % (len(scoreDocs))

    maxf = []
    maxrank = -1000.0
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        filename = doc.get('filename')
        rank = ranker(command_dict, getInfo(folders, readers, filename))
        if rank > maxrank:
            maxf = [filename]
            maxrank = rank
        elif rank == maxrank:
            maxf.append(filename)
    
    del searcher
    
    if len(maxf) == 0:
        print "error in searchtrip.py: no result while searching", command_dict.get('location', '')
        return "Interior Error"
    elif len(maxf) != 1:
        print "warning in searchtrip.py: multiple results when searching", command_dict.get('location', '')
    return getInfo(folders, readers, maxf[0])

def ranker(command_dict, info):
    '''rank all search results | the location evidence needs to be modified, consider content relativity more | 2017-12-01'''
    cmd_loc = command_dict.get('location')
    #evidence1-location evidence
    loc_evd = 0.0
    location = info.get('location', '')
    location = unicode(location, 'utf8', 'ignore')
    cmd_loc = jieba.cut(cmd_loc)
    for loc in cmd_loc:
        if loc in location:
            loc_evd += 40.0
    #evidence2-introduction evidence
    intro_evd = 0.0
    introduction = info.get('introduction', '')
    if introduction != '':
        intro_evd = math.log(len(introduction)+1)
    #evidence3-score evidence
    score_evd = 0.0
    score = info.get('score', '')
    if score != '':
        score_evd = float(score)
    res = loc_evd+intro_evd+score_evd
    print location, res
    return res 

def constructReaders(folders):
    res = {}
    for folder in folders:
        res[folder] = Reader(folders[folder])
    return res

def getInfo(folders, readers, filename):
    '''get all information from a file'''
    res = {}
    special_tags = ['introduction']
    for folder in folders:
        try:
            path = os.path.join(folder, filename)
            f = open(path, 'r')
            content = f.read()
            f.close()
            readers[folder].match(content)
            for attr in folders[folder]:
                tmp = readers[folder].get(attr).strip()
                if tmp != 'None' and tmp != '' and tmp != '\n':
                    if attr in special_tags:
                        res[attr] = res.get('attr','')+'\n'+folder+'\n'+tmp
                    elif attr != 'location':
                        res[attr] = res.get('attr', '') + tmp
                    else:
                        res['location'] = tmp
        except Exception, e:
            continue
    #print res.get('introduction', 'None')
    return res

if __name__ == '__main__':
    run()
