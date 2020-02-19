# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 19:45:14 2020

@author: zhaoj
"""

import pandas as pd
import numpy as np
import json

with open('./article_list.json') as f:
    raw_list = json.load(f)
    

l_type = []
l_title = []
l_author = []
l_searched_author = []
l_cite = []
l_link = []
l_journal = []

for a in raw_list:
    for pp in raw_list[a]:
        pbib = pp['bibtex']
        if not 'type' in pbib:
            continue
        lt = pbib['type']
        lti = 'null'
        if 'title' in pbib:
            lti = pbib['title']
        la = 'null'
        if 'author' in pbib:
            la = str(pbib['author'])
        ls = a
        lc = pp['cite_count']
        ll = pp['link']
        lj = 'null'
        if 'journal' in pbib:
            lj = pbib['journal']
        l_type.append(lt)
        l_title.append(lti)
        l_author.append(la)
        l_searched_author.append(ls)
        l_cite.append(lc)
        l_link.append(ll)
        l_journal.append(lj)
        
l_dict = {'type': l_type, 'title': l_title, 'author': l_author, 'searched_author': l_searched_author, 
          'citation': l_cite, 'link': l_link, 'journal': l_journal}

d = pd.DataFrame(l_dict)
d.to_excel('article_list.xls')