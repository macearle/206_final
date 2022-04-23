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
import re


def make_request(song_lst): 
    matches = []
    songs = []
    genres = []
    count = 0
    reg_exp_feat = r"(^.*) Feat.*"
    reg_exp_parenth = r"(^.*) \(.*"
    for item in song_lst:
        #reg ex song
        full_song = item[0]
        if full_song[0] == '(':
            starts_with_p = r"\(.*\) (.*)"
            song = re.findall(starts_with_p,full_song)[0]
        elif ')' == full_song[-1]:
            song = re.findall(reg_exp_parenth,full_song)[0]
        else:
            song = full_song
        #reg ex artist
        full_artist = item[1]
        if "Feat" in full_artist:
            artist = re.findall(reg_exp_feat,full_artist)[0]
        else:
            artist = full_artist
        
        year = item[2]
        #print(song,artist,year)
        #print(count)
        r = requests.get("https://itunes.apple.com/search", params = {'term': song,'media': 'music'})
        result = json.loads(r.text)
        for item in result['results']:
            if item['artistName'] in artist:
                if song in songs:
                    continue
                else:
                    songs.append(song)
                    #print(item)
                    count += 1
                    genre = item['primaryGenreName']
                    genres.append((song,genre))
    return genres


def create_grene_table(genres):
   cur, conn = createDatabase('Top100Songs.db')
   cur.execute("CREATE TABLE IF NOT EXISTS genres (genreid INTEGER PRIMARY KEY, genre STRING)")

   only_genre = []
   for genre in genres:
       if genre not in only_genre:
           only_genre.append(genre[1])
       else:
            continue
    
   for i in range(len(only_genre)):
      #print(i)
      #print(artistnames[i])
      cur.execute("INSERT OR IGNORE INTO genres (genreid, genre) VALUES (?,?)",(i, only_genre[i]))
      conn.commit()


song_lst = get_links()
print(make_request(song_lst))
print(len(make_request(song_lst)))


#create_grene_table(genres)

#info['artistName'] == artist and 