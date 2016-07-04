# -*- coding: utf8 -*-
u'''
@summary:
@author: cshanxiao
@date: 2016年7月3日
'''
import simplejson

class DataUtil(object):
    
    def __init__(self):
        pass
    
    def save_movie_info(self, movie_info):
        info = {"info_url": "",
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
        info.update(movie_info)
        save_path = "./data/movies.txt"
        with open(save_path, "a") as fd:
            fd.write(simplejson.dumps(info) + "\n")
        
        