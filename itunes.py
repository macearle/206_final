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
                    genres.append((song, genre))
    return


song_lst = get_links()
print(make_request(song_lst))