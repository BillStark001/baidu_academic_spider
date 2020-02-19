# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 17:16:23 2020

@author: billstark001
"""
from urllib.parse import quote, unquote
from selenium import webdriver
from bs4 import BeautifulSoup
import json

def get_bibtex(driver, url, sign=0, template='http://xueshu.baidu.com/u/citation?&url={}&sign={}&t=bib', retry=3):
    final_url = template.format(quote(url, 'utf-8'), sign)
    driver.get(final_url)
    content = None
    for i in range(max(retry, 1)):
        try:
            content = driver.page_source.split('wrap;">')[1].split('</pre')[0]
        except Exception as e:
            print(driver.page_source, e)
        if content is not None:
            break
    return content

def form_search(*names, template = 'http://xueshu.baidu.com/s?wd=author%3A%28{0}%29'):
    filtrated_names = [quote(x, encoding='utf-8') for x in names]
    return template.format(*filtrated_names)

def parse_bibtex(bib):
    if isinstance(bib, dict):
        return bib
    if not isinstance(bib, str):
        return {}
    
    m1 = bib.find('@')
    m3 = bib.find(',')
    m2 = bib.find('{')
    m4 = bib.rfind('}')
    ans_dict = {}
    ans_dict['type'] = bib[m1 + 1: m2]
    ans_dict['name'] = bib[m2 + 1: m3]
    content = bib[m3 + 1: m4]
    content = content.replace('\n', '').split('=')
    for i in range(len(content) - 1):
        cont_name = content[i]
        cont_name_mark = cont_name.rfind(',')
        if not cont_name_mark == -1:
            cont_name = cont_name[cont_name_mark + 1:]
        cont_name = cont_name.replace(' ', '')
        cont = content[i + 1]
        cont_m1 = cont.find('{')
        cont_m2 = cont.rfind('}')
        cont = cont[cont_m1 + 1: cont_m2]
        # special parse
        if cont_name in ['author', 'authors']:
            cont = cont.split('and')
            cont = [x.strip(' ') for x in cont]
        elif cont_name in ['number', 'numners', 'year', 'volume']:
            try:
                cont = int(cont)
            except Exception as e:
                print(cont_name, e)
                cont = cont
        elif cont_name in ['page', 'pages']:
            cont_ = cont
            try:
                cont = cont.split('-')
                if len(cont) == 2:
                    cont = [int(cont[0]), int(cont[1])]
                elif len(cont) == 1:
                    cont = [int(cont[0]), int(cont[0])]
            except Exception as e:
                print(cont_name, cont_, e)
                cont = cont_
        ans_dict[cont_name] = cont
    return ans_dict

def get_bibs(driver, author):
    
    test_str = form_search(author)

    driver.get(test_str + '&pn=500')

    html = driver.page_source
    bf_base_page = BeautifulSoup(html, 'lxml')
    try:
        max_page = bf_base_page.find_all(class_='pc')[-1]
        pages = int(max_page.contents[0])
    except:
        pages = 1
    procs = []
    for cur_page in range(pages):
        cur_pn = cur_page * 10
        driver.get(test_str + '&pn=%d'%cur_pn)
        bf_base_page = BeautifulSoup(driver.page_source, 'lxml')
        articles = bf_base_page.find_all(class_='result sc_default_result xpath-log')
        for atc in articles:
            site_cont_r = atc.find_all(class_='sc_cite_cont')
            quotation_r = atc.find_all(class_='sc_q c-icon-shape-hover', title='引用')
            if len(site_cont_r) == 0 or len(quotation_r) == 0:
                continue
            else:
                scont = site_cont_r[0].contents[0].replace('\n', '').replace(' ', '')
                if scont.endswith('万'):
                    scont = int(float(scont[:-1]) * 10000)
                quot = quotation_r[0].attrs
                proc = dict(cite_count=int(scont), link=quot['data-link'], baidu_sign=quot['data-sign'])
                procs.append(proc)
    
    ans = []
    for qattr in procs:
        bib = get_bibtex(driver, qattr['link'], qattr['baidu_sign'])
        qattr['bibtex'] = parse_bibtex(bib)
        ans.append(qattr)
        
    return ans

if __name__ == '__main__':
    with open('./author_list.txt', encoding='utf-8') as f:
        authors = [x[:-1].split(',')[0] for x in f.readlines()]
        
    options = webdriver.ChromeOptions()
    #options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"')
    options.add_argument('user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36"')
    driver = webdriver.Chrome('chromedriver80.exe', options=options)
    
    #bibs = {}
    for author in authors[24:]:
        #flag = False
        #while not flag:
        #    try:
        bibs[author] = get_bibs(driver, author)
        #        flag = True
        #    except Exception as e:
        #        print(e)
        with open('./article_list.json', 'w') as f:
            json.dump(bibs, f, indent=2)
    