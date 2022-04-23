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


def make_request(song_lst): 
    matches = []
    songs = []
    for item in song_lst:
        song = item[0]
        artist = item[1]
        year = item[2]
        r = requests.get("https://itunes.apple.com/search", params = {'term': song,
                                            'media': 'music'})
        result = json.loads(r.text)
        for info in result['results']:
            if info['artistName'] == artist and info['trackName'] == song and info['kind'] == 'song' and (year in info['releaseDate']):
                if song in songs:
                    continue
                else:
                    songs.append(song)
                    print(info)
    #                 album = info['collectionName']
    #                 releasedate = info['releaseDate']
    #                 country = info['country']
    #                 genre = info['primaryGenreName']
    #                 full_song_data = {}
    #                 full_song_data['song'] = song
    #                 full_song_data['album'] = album
    #                 full_song_data['album'] = album
    #                 full_song_data['releasedate'] = releasedate
    #                 full_song_data['country'] = country
    #                 full_song_data['genre'] = genre
    #                 matches.append(full_song_data)
    # return matches

song_lst = get_links()
print(make_request(song_lst))