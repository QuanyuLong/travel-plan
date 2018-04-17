#!/usr/bin/env python
# -*- coding:utf-8 -*-
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time, jieba, math
from eicReader import Reader
from datetime import datetime
from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file content.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

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

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):

        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        reader = Reader()
        idealp = 100 #设置理想价格
        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
#                if not filename.endswith('.txt'):
#                    continue
                
                print "adding", filename
                try:

                    path = os.path.join(root, filename)

                    file = open(path)
                    content = unicode(file.read().strip('\n'), 'utf8', 'ignore')
                    file.close()
                    
                    reader.match(content)
                    food = reader.getstr('img_list')
                    foodshop = reader.getstr('name')
                    foodshop = "\t".join(jieba.cut(foodshop)) + '\t' + foodshop
                    tel = reader.getstr('tel')
                    location = reader.getstr('location')
                    environment_score = reader.get('environment_score',0)
                    flavour_score = reader.get('flavour_score',0)
                    service_score = reader.get('service_score',0)
                    price_level = reader.get('price_level',0)
                    
                    #计算评分
                    Sum = environment_score + flavour_score + service_score
                    thegema = math.fabs(price_level - idealp)
                    rank = Sum/3 + math.pow(math.e, -thegema)
                    
                    doc = Document()
                    doc.add(Field("province", root, t1))                #所在省份

                    doc.add(Field("foodshop", foodshop, t1))            #商家名
                    doc.add(Field("food", food, t1))                    #食品名（用\t分割）
                    doc.add(Field("location", location, t1))            #地址
                    doc.add(Field("tel", tel, t1))                      #电话号码
                    doc.add(Field("environment_score", str(environment_score), t1))  #环境评分
                    doc.add(Field("service_score", str(service_score), t1))          #服务评分
                    doc.add(Field("flavour_score", str(flavour_score), t1))          #口味评分
                    doc.add(Field("price_level", str(price_level), t1))              #人均价格
                    doc.add(Field("rank", str(rank), t1))                            #rank
                    if len(content) > 0:
                        doc.add(Field("content", content, t2))
                    else:
                        print "warning: no content in %s" % filename
                    writer.addDocument(doc)
                except Exception, e:
                    print "Failed in indexDocs:", e


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
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        IndexFiles('shanghai', "index", analyzer)
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e
