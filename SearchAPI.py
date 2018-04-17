#!/usr/bin/env python
#encoding: utf-8
#file: SearchAPI.py

from searchtrip import search_trip
from Search_Dping import search_dianping

def Search (province, kind, query):
    '''search api'''
    if kind == 'trip':
        query = unicode (query, 'utf8', 'ignore')
        return search_trip(query)
    elif kind == 'food' or kind == 'foodshop':
        return search_dianping(province, kind, query)
    #print search_trip(query)
    
if __name__ == "__main__":
    #note: <province> shanghai for search_dianping
    Search('shanghai','food','大虾')
