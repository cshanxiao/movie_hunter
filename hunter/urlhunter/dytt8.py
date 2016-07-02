# -*- coding: utf8 -*-
u'''
@summary:
@author: cshanxiao
@date: 2016年7月3日
'''
import os
import threading

from bs4 import BeautifulSoup
import requests

from hunter.log.logconfig import dytt8log as log
from hunter.urlhunter.ispider import ISpider


file_lock = threading.Lock()

class Dytt8Spider(ISpider):

    def __init__(self):
        self.base_url = "http://www.dytt8.net"
        self.sess = requests.session()
        
    def parse_index(self):
        index_content = self.sess.get(self.base_url).content
        dom = BeautifulSoup(index_content, "lxml")
        tag_div_menu = dom.find_all("div", {"id": "menu"})
        
        menu_urls = {}
        tag_a = tag_div_menu[0].find_all("a")
        for url in tag_a:
            menu_urls[url.text] = url["href"]
            log.info("movie_type: %s, url: %s",url.text, url["href"]) 
        log.info(menu_urls)
        
        for movie_type, url in menu_urls.iteritems():
            if url in ["#", "index.html"]:
                log.info("ignore movie_type: %s, url: %s", url.text, url["href"])
                continue
            self.parse_movie_list(movie_type, url)
            break
            
    def _parse_list(self, content):
        page_urls = []
        with file_lock:
            with open("./tmp.txt", "w") as fd:
                fd.write(content)
        
            with open("./tmp.txt", "r") as fd:
                for line in fd.readlines():
                    line = line.strip()
                    if not "option" in line:
                        continue
                    
                    try:
                        tag_option = BeautifulSoup(line, "lxml")
                        page = int(tag_option.text)
                        url = tag_option.body.option["value"]
                        log.info("page: %s, url: %s", page, url)
                        page_urls.append([page, url])
                    except:
                        pass
            os.remove("./tmp.txt")
        return page_urls
        
    def parse_movie_list(self, movie_type, url):
        try:
            if not url.startswith("http"):
                url = "".join([self.base_url, url])
            url_pre = url.rsplit("/", 1)[0]
            log.info("url_pre: %s", url_pre)
            content = self.sess.get(url).content
            page_urls = self._parse_list(content)
            for page, page_url in page_urls:
                page_url = "/".join([url_pre, page_url])
                print page_url
                break
            
        except Exception:
            log.error("parse_movie_list failed! movie_type: %s, url: %s", 
                      movie_type, url, exc_info=True)
        
    def parse_movie_info(self):
        pass
        
    
    
    