#!usr/bin/env python

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time, jieba, urllib
from datetime import datetime
from bs4 import BeautifulSoup
from eicreader import Reader

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

def get_domain(url):
    res = []
    proto, rest = urllib.splittype(url)
    host, rest = urllib.splithost(rest)
    if host:
        host = host.split('.')
        if len(host) >= 2:
            ind = len(host) - 2
            ans = host[-1]
            while ind >= 0:
                ans = host[ind]+'.'+ans
                res.append(ans)
                ind -= 1
            return ' '.join(res)
        else:
            return host
    else:
        return 'unknown'

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        
        self.folders = {'parsed_ctrip':['source', 'location', 'introduction', 'score', 'img_list'],
                        'parsed_qunar':['location', 'rank', 'score', 'time', 'introduction', 'img_list'],
                        'eic_mfw':['location', 'introduction', 'img_list']}
        self.special_tags = ['introduction']
        self.files = self.__getAllPlaces()
        #self.readers = self.__constructReaders()

        self.indexDocs(writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, writer):
        for filename in self.files:
            print "adding", filename
            try:
                doc = Document()
                doc.add(Field('location', 
                                ' '.join(jieba.cut(unicode(filename[:-4], 'utf-8', 'ignore'))),
                                                Field.Store.NO,
                                                Field.Index.ANALYZED))
                doc.add(Field('filename', unicode(filename, 'utf-8', 'ignore'),
                                                Field.Store.YES,
                                                Field.Index.NOT_ANALYZED))
                
                writer.addDocument(doc)
            
            except Exception, e:
                print "Failed in indexDocs:", e
    
    def __constructReaders(self):
        res = {}
        for folder in self.folders:
            res[folder] = Reader(self.folders[folder])
        return res
    
    def __getAllPlaces(self):
        res = set()
        for folder in self.folders:
            for root, dirnames, filenames in os.walk(folder):
                res = res | set(filenames)
        #print res
        return list(res)
        
    def __getInfo(self, filename):
        '''get all information from a file'''
        res = {}
        for folder in self.folders:
            try:
                path = os.path.join(folder, filename)
                f = open(path, 'r')
                content = f.read()
                f.close()
                self.readers[folder].match(content)
                for attr in self.folders[folder]:
                    tmp = self.readers[folder].get(attr).strip()
                    if tmp != 'None' and tmp != '' and tmp != '\n':
                        if attr in self.special_tags:
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
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        IndexFiles("index_trip", analyzer)
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e
