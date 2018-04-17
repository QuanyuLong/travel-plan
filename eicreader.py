#!/usr/bin/env python
#encoding: utf-8
#file: eicreader.py

import re

class Reader:
    def __init__(self, attrs, default = 'None'):
        self.re_str = ''
        for attr in attrs:
            self.re_str += '(?P<'+attr+'><'+attr+'>.*?</'+attr+'>)?\n?'
        #print self.re_str
        self.pattern = re.compile(self.re_str, re.S)
        self.tag_pattern = re.compile(r'</?.*?>')
        self.info = None
        self.default = default
        
    def match(self, s):
        '''return a dict with all information'''
        #print 's', s
        mat = self.pattern.match(s)
        self.info = mat.groupdict(self.default)
        return self.info
        
    def get(self, tag):
        '''AFTER MATCH, use get to extract information'''
        if self.info == None:
            print '<warning> no information matched yet. Please use match function. Returning default(', \
                  self.default, ')'
            return self.default
        val = self.info.get(tag, '')
        if val == '':
            print '<warning> no tag', tag, 'found in reader. Returning default(', \
                    self.default, ')'
            return self.default
        return self.remove_tag(val)
    
    def remove_tag(self, tagged):
        '''remove tag from tagged(type str)'''
        return self.tag_pattern.sub('', tagged)
        
if __name__ == "__main__":
    test = '<source>http://you.ctrip.com/sight/shanghai2/3309460.html</source><location>功夫\n茶馆</location>'
    tags = ['source', 'location', 'introduction', 'score', 'img_list']
    reader = Reader(tags)
    reader.match(test)
    print reader.get('source')
    print reader.get('location')
    print reader.get('introduction')
