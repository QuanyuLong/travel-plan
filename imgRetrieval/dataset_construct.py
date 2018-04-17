#!/usr/bin/env python
#encoding: utf-8
#file: imgIndex.py
import os
from eicReader import*
import color_descriptor
import structure_descriptor
import glob
import argparse
import cv2
import urllib

def get_info_from_eic(filename):
    """从一个eic文件中获取imgurl,并返回一个URL列表"""
    tags = ['source', 'location', 'introduction', 'score', 'img_list']
    reader = Reader(tags)
    content = open(filename).read()
    reader.match(content)
    return reader.get('location').strip(), reader.get('img_list').split('\n')[1:-1]


    

def datasetConstruct(eicroot):
    """从eicroot中读取imgurl,然后将相应的图片下载到本地"""
    dataset = os.path.join(os.getcwd(),'dataset')
    eicroot = os.path.join(os.getcwd(),eicroot)
    if not os.path.exists(eicroot):
        print 'no such eicroot!'
        return 
    for root,dirs,files in os.walk(eicroot,topdown=True):
        for filename in files:
            print 'adding ' + filename
            if not filename.endswith('.eic'):
                continue
            path = os.path.join(root, filename)
            location,url_list = get_info_from_eic(path)
            for idx, url in enumerate(url_list):
                imgName = location + '_' + str(idx) + '.jpg'
                downloadpath = os.path.join(dataset,imgName)
                urllib.urlretrieve(url, downloadpath) 



if __name__ == '__main__':
    datasetConstruct('parsed_ctrip')
