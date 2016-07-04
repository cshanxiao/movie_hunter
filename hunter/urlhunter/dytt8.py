# -*- coding: utf8 -*-
u'''
@summary:
@author: cshanxiao
@date: 2016年7月3日
'''
import os
import uuid

from bs4 import BeautifulSoup

from hunter.common.config import MIN_IMDB_SCORE, MAX_IMDB_SCORE
from hunter.common.datautil import DataUtil
from hunter.log.logconfig import dytt8log as log
from hunter.urlhunter.ispider import ISpider


class Dytt8Spider(ISpider):

    def __init__(self):
        ISpider.__init__(self)
        self.base_url = "http://www.dytt8.net"
        self.datautil = DataUtil()
        
    def parse_index(self):
        index_content = self.sess.get(self.base_url).content
        dom = BeautifulSoup(index_content, "lxml")
        tag_div_menu = dom.find_all("div", {"id": "menu"})
        
        menu_urls = {}
        tag_a = tag_div_menu[0].find_all("a")
        for url in tag_a:
            menu_urls[url.text] = url["href"]
            log.info("movie_type: %s, url: %s", url.text, url["href"]) 
        log.info(menu_urls)
        
        for movie_type, url in menu_urls.iteritems():
            if url in ["#", "index.html"]:
                log.info("ignore movie_type: %s, url: %s", url.text, url["href"])
                continue
            self.parse_movie_list(movie_type, url)
    
    def _get_temp_filename(self):
        return "./data/tmp/tmp_%s.txt" % str(uuid.uuid4())
    
    def _parse_list(self, content):
        page_urls = []
        file_name = self._get_temp_filename()
        with open(file_name, "w") as fd:
            fd.write(content)
        
        with open(file_name, "r") as fd:
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
        os.remove(file_name)
        return page_urls
        
    def parse_movie_list(self, movie_type, url):
        try:
            if not url.startswith("http"):
                url = "".join([self.base_url, url])
            url_pre = url.rsplit("/", 1)[0]
            log.info("url_pre: %s", url_pre)
            content = self.random_delay_get(url).content
            page_urls = self._parse_list(content)
            for page, page_url in page_urls:
                page_url = "/".join([url_pre, page_url])
                self.parse_movie_info(page, page_url)
            
        except Exception:
            log.error("parse_movie_list failed! movie_type: %s, url: %s",
                      movie_type, url, exc_info=True)
        
    def parse_movie_info(self, page, page_url):
        try:
            content = self.random_delay_get(page_url).content
            file_name = self._get_temp_filename()
            with open(file_name, "w") as fd:
                fd.write(content)
            
            movie_urls = []
            with open(file_name, "r") as fd:
                lines = fd.readlines()
                for line in lines:
                    line = line.strip()
                    if not "ulink" in line:
                        continue
                    dom = BeautifulSoup(line, "lxml")
                    movie_urls.append(dom.body.a["href"])
            os.remove(file_name)

            url_pre = page_url.split("/html", 1)[0]
            log.info("url_pre: %s", url_pre)
            for movie_url in movie_urls:
                movie_url = "".join([url_pre, movie_url])
                self.parse_movie_detail_info(movie_url)
                
        except Exception:
            log.error("parse_movie_info failed! page: %s, page_url: %s",
                      page, page_url, exc_info=True)
    
    def _pasrse_detail(self, file_name, movie_info):
        with open(file_name, "r") as fd:
            lines = fd.readlines()
            for line in lines:
                line = line.strip()
                
                if "ftp://" in line:
                    dom = BeautifulSoup(line, "lxml", from_encoding="gb2312")
                    href = dom.body.td.a["href"]
                    movie_info["download_urls"].append(href)
                elif not line.startswith('''<p><img border="0"'''):
                    continue
                try:
                    line = line.decode("gb2312").encode("utf8")
                except:
                    try:
                        line = line.encode("utf8")
                    except:
                        pass
                    
                text = line.split("<br />")
                for item in text:
                    item = item.strip()
                    if not item:
                        continue
                    
                    if isinstance(item, unicode):
                        item = item.encode("utf8")
#                         elif isinstance(item, str):
#                             pass
                    else:
                        try:
                            item = item.decode("gb2312").encode("utf8")
                        except:
                            pass

                    tmp_item = item.replace(" ", "")
                    try:
                        tmp_item = item.replace("\xe3\x80\x80", "")                        
                        tmp_item = tmp_item.decode("utf8")
                    except:
                        tmp_item = tmp_item.decode("utf8")
                    
                    if tmp_item.startswith(u"◎译名"):
                        movie_info["translated_name"] = tmp_item.split(u"◎译名")[1].strip()
                    elif tmp_item.startswith(u"◎片名"):
                        movie_info["name"] = tmp_item.split(u"◎片名")[1].strip()
                    elif tmp_item.startswith(u"◎年代"):
                        movie_info["year"] = tmp_item.split(u"◎年代")[1].strip()
                    elif tmp_item.startswith(u"◎国家"):
                        movie_info["country"] = tmp_item.split(u"◎国家")[1].strip()
                    elif tmp_item.startswith(u"◎类别"):
                        movie_info["tags"] = tmp_item.split(u"◎类别")[1].strip()
                    elif tmp_item.startswith(u"◎语言"):
                        movie_info["language"] = tmp_item.split(u"◎语言")[1].strip()
                    elif tmp_item.startswith(u"◎字幕"):
                        movie_info["subtitles"] = tmp_item.split(u"◎字幕")[1].strip()
                    elif tmp_item.startswith(u"◎IMDb评分"):
                        movie_info["IMDb"] = tmp_item.split(u"◎IMDb评分")[1].strip()
                        text = tmp_item.split(u"◎IMDb评分")[1].strip()
                        movie_info["IMDb"] = float(text.split("/")[0].strip())
                        movie_info["IMDb_total"] = int(float(text.split(" ")[0].split("/")[1].replace("&nbsp;", "").strip()))
                        movie_info["IMDb_users_count"] = int(float(text.split(" ")[2].replace(",", "")))
                    elif tmp_item.startswith(u"◎文件格式"):
                        movie_info["file_format"] = tmp_item.split(u"◎文件格式")[1].strip()
                    elif tmp_item.startswith(u"◎视频尺寸"):
                        movie_info["size"] = tmp_item.split(u"◎视频尺寸")[1].strip()
                    elif tmp_item.startswith(u"◎文件大小"):
                        movie_info["file_size"] = tmp_item.split(u"◎文件大小")[1].strip()
                    elif tmp_item.startswith(u"◎片长"):
                        movie_info["film_length"] = tmp_item.split(u"◎片长")[1].strip()
                    elif tmp_item.startswith(u"◎导演"):
                        movie_info["director"] = tmp_item.split(u"◎导演")[1].strip()
                    elif tmp_item.startswith(u"◎主演"):
                        movie_info["actors"] = [tmp_item.split(u"◎主演")[1].strip()]
    
    def parse_movie_detail_info(self, movie_url):
        try:
            content = self.random_delay_get(movie_url).content
            file_name = self._get_temp_filename()
            with open(file_name, "w") as fd:
                fd.write(content.replace("\r", "\n"))
            
            movie_info = {"info_url": movie_url,
                          "title": "",
                          "translated_name": "",
                          "name": "",
                          "year": "",
                          "country": "",
                          "tags": [],
                          "language": "",
                          "subtitles": "",
                          "IMDb": 0,
                          "IMDb_total": 10,
                          "IMDb_users_count": 0,
                          "file_format": "",
                          "size": "",
                          "file_size": "",
                          "film_length": "",
                          "director": "",
                          "actors": [],
                          "download_urls": []
                          }
            
            
            os.remove(file_name)
            
            if not MIN_IMDB_SCORE <= movie_info["IMDb"] <= MAX_IMDB_SCORE:
                return
            self.datautil.save_movie_info(movie_info)
        except Exception:
            log.error("parse_movie_detail_info failed! movie_url: %s",
                      movie_url, exc_info=True)

    
    
