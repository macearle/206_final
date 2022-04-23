from aem import con
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
        full_song = item[0]
        if full_song[0] == '(':
            starts_with_p = r"\(.*\) (.*)"
            song = re.findall(starts_with_p,full_song)[0]
        elif ')' == full_song[-1]:
            song = re.findall(reg_exp_parenth,full_song)[0]
        else:
            song = full_song
        full_artist = item[1]
        if "Feat" in full_artist:
            artist = re.findall(reg_exp_feat,full_artist)[0]
        else:
            artist = full_artist
        year = item[2]

        r = requests.get("https://itunes.apple.com/search", params = {'term': song,'media': 'music'})
        result = json.loads(r.text)
        for item in result['results']:
            if item['artistName'] in artist:
                if song in songs:
                    continue
                else:
                    songs.append(song)
                    count += 1
                    genre = item['primaryGenreName']
                    genres.append((song,genre))
    return genres


def create_grene_table(genres):
   cur, conn = createDatabase('Top100Songs.db')
   cur.execute("CREATE TABLE IF NOT EXISTS genres (genreid INTEGER PRIMARY KEY, genre STRING)")
   big_genre_lst = []
   for item in genres:
       big_genre_lst.append(item[1])
   only_genre = []
   for genre in big_genre_lst:
       if genre in only_genre:
           continue
       else:
            only_genre.append(genre)

   for i in range(len(only_genre)):
      cur.execute("INSERT OR IGNORE INTO genres (genreid, genre) VALUES (?,?)",(i, only_genre[i]))
      conn.commit()

def all_data(songinfo, genres):
    data = []
    rank = 100
    for songs in genres:
        song = songs[0]
        genre = songs[1]
        for item in songinfo:
            if song == item[0]:
                artistname = item[1]
                year = item[2]
        data.append((song, genre, artistname,year, rank))
        rank -= 1
    return data

def create_songdata_table(alldata): 
    cur, conn = createDatabase('Top100Songs.db')
    cur.execute('CREATE TABLE IF NOT EXISTS songdata(rank INTEGER PRIMARY KEY, songtitle STRING, year INTEGER, artistid INTEGER, genreid INTEGER)')
    for songs in alldata:
        song = songs[0]
        genre_ = songs[1]
        cur.execute("SELECT genreid FROM genres WHERE genre = ?", (genre_,))
        gid = int(cur.fetchone()[0])
        artistname = songs[2]
        cur.execute("SELECT artistid FROM artists WHERE artistname = ?", (artistname,))
        id = int(cur.fetchone()[0])
        year = songs[3]
        rank = songs[4]
        cur.execute('INSERT OR IGNORE INTO songdata(rank, songtitle, year, artistid, genreid) VALUES (?,?,?,?,?)', (rank, song, year, id, gid))
    conn.commit()
 


song_lst = get_links()
genres = make_request(song_lst)
create_grene_table(genres)
data = all_data(song_lst, genres)
create_songdata_table(data)


