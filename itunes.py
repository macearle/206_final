import requests, json
from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
from itertools import count
import matplotlib.pyplot as plt
import sqlite3
import numpy as np
from sqlalchemy import values
from top100songs import get_links
from top100songs import createDatabase


def make_request(song_lst): 
    matches = []
    songs = []
    genres = []
    for item in song_lst:
        song = item[0]
        artist = item[1]
        year = item[2]
        r = requests.get("https://itunes.apple.com/search", params = {'term': song,
                                            'media': 'music'})
        
        result = json.loads(r.text)
        for info in result['results']:
            if info['artistName'] == artist and info['trackName'] == song and info['kind'] == 'song':
                if song in songs:
                    continue
                else:
                    songs.append(song)
                    #print(info)
                    genre = info['primaryGenreName']
                    if genre not in genres:
                        genres.append(genre)
                    else:
                        continue
    return genres


def create_grene_table(genres):
   cur, conn = createDatabase('Top100Songs.db')
   cur.execute("CREATE TABLE IF NOT EXISTS genres (genreid INTEGER PRIMARY KEY, genre STRING)")

   for i in range(len(genres)):
      #print(i)
      #print(artistnames[i])
      cur.execute("INSERT OR IGNORE INTO genres (genreid, genre) VALUES (?,?)",(i, genres[i]))
      conn.commit()


song_lst = get_links()
genres = make_request(song_lst)
create_grene_table(genres)