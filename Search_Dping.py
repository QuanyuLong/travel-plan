#!/usr/bin/env python
#encoding: utf8
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, math

from initVM import *
from java.io import File
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
search query entered against the 'content' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
def parseCommand(command):
    '''
    input: C title:T author:A language:L
    output: {'content':C, 'title':T, 'author':A, 'language':L}

    Sample:
    input:'contenance title:henri language:french author:william shakespeare'
    output:{'author': ' william shakespeare',
                   'language': ' french',
                   'content': ' contenance',
                   'title': ' henri'}
    '''
    allowed_opt = ['food', 'foodshop']
    command_dict = {}
    opt = 'food'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = command_dict.get(opt, '') + ' ' + value
        else:
            command_dict[opt] = command_dict.get(opt, '') + ' ' + i
    return command_dict

def run(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."

        command = raw_input("Query:")
        #command = unicode(command, 'GBK')
        command = unicode(command, 'utf8')
        if command == '':
            return

        print
        print 'searching for : ' + command
        command_dict = parseCommand(command)
        querys = BooleanQuery()
        for k,v in command_dict.iteritems():
            query = QueryParser(Version.LUCENE_CURRENT, k,
                                analyzer).parse(v)
            querys.add(query, BooleanClause.Occur.MUST)
        scoreDocs = searcher.search(querys, 50).scoreDocs
        print "%s total matching documents." % len(scoreDocs)
        
        #比较评分
        max_rank = 0
        best_shop = ''
        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            cur_shop = doc.get("foodshop").split()[-1]
            cur_rank = float(doc.get('rank'))
            if cur_rank > max_rank:
                max_rank = cur_rank
                best_shop = cur_shop
        result = {}
        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            cur_shop = doc.get("foodshop").split()[-1]
            cur_rank = float(doc.get('rank'))
            
            if cur_rank == max_rank:
                result['name'] = cur_shop.encode('utf8','ignore')
                result['rank'] = doc.get('rank').encode('utf8','ignore')
                result['food'] = doc.get('food').encode('utf8','ignore')
                result['location'] = doc.get('location').encode('utf8','ignore')
                result['tel'] = doc.get('tel').encode('utf8','ignore')
                result['environment_score'] =  doc.get('environment_score').encode('utf8','ignore')
                result['flavour_score'] = doc.get('flavour_score').encode('utf8','ignore')
                result['service_score'] = doc.get('service_score').encode('utf8','ignore')
                result['price_level'] = doc.get('price_level').encode('utf8','ignore')
        print result
        
def search_dianping(province, kind, query):
    STORE_DIR = "index"
    vm_env.attachCurrentThread()
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    
    allowed_opt = ['food', 'foodshop']
    
    if kind not in allowed_opt:
        return None
    if query == '':
        return None
        
    command = '%s:%s province:%s' %(kind, query, province)
    command = unicode(command, 'utf8','ignore')
    command_dict = parseCommand(command)
    querys = BooleanQuery()
    for k,v in command_dict.iteritems():
        query = QueryParser(Version.LUCENE_CURRENT, k,
                            analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST)
    scoreDocs = searcher.search(querys, 50).scoreDocs
    #比较评分
    max_rank = 0
    best_shop = ''
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        cur_shop = doc.get("foodshop").split()[-1]
        cur_rank = float(doc.get('rank'))
        if cur_rank > max_rank:
            max_rank = cur_rank
            best_shop = cur_shop
            
    result = {}
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        cur_shop = doc.get("foodshop").split()[-1]
        cur_rank = float(doc.get('rank'))
        
        if cur_rank == max_rank:
            result['name'] = cur_shop.encode('utf8','ignore')
            result['rank'] = doc.get('rank').encode('utf8','ignore')
            result['food'] = doc.get('food').encode('utf8','ignore')
            result['location'] = doc.get('location').encode('utf8','ignore')
            result['tel'] = doc.get('tel').encode('utf8','ignore')
            result['environment_score'] =  doc.get('environment_score').encode('utf8','ignore')
            result['flavour_score'] = doc.get('flavour_score').encode('utf8','ignore')
            result['service_score'] = doc.get('service_score').encode('utf8','ignore')
            result['price_level'] = doc.get('price_level').encode('utf8','ignore')
    
    del searcher
    return result

if __name__ == '__main__':
#    STORE_DIR = "index"
#    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
#    print 'lucene', lucene.VERSION
#    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
#    directory = SimpleFSDirectory(File(STORE_DIR))
#    searcher = IndexSearcher(DirectoryReader.open(directory))
#    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
#    run(searcher, analyzer)
#    del searcher
    print search_dianping('shanghai', 'food', '大虾')
