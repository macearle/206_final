from operator import index
import requests, json
from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import sqlite3
import json
import os


def get_links():
   """
   This function uses the top 100 songs of all time website and 
   pulls the song title, artist name, and year released for every 
   song in the list of top 100 songs using BeautifulSoup. We created a list 
   of tuples, one for each song with this information. 
   """
   url = 'https://top40weekly.com/top-100-songs-of-all-time/'
   request = requests.get(url)
   soup = BeautifulSoup(request.content, "html.parser")
   song_scrape = soup.find_all('div', class_ = 'x-text song-title')
   artist_scrape = soup.find_all('div', class_ = 'x-text artist-name')
   year_scrape = soup.find_all('div', class_ = 'x-text song-rel')
   songs = []

   for index in range(len(song_scrape)):
       a = (song_scrape[index])
       b = (artist_scrape[index])
       c = (year_scrape[index])
       song = a.text.strip()
       artist = b.text.strip()
       year = c.text.strip()
       
       index +=1
       tup = (song,artist,year[-4:])
       songs.append(tup)
   return songs
# print(len(get_links()))


def get_artistnames(data):
   """
   This function takes the list of tuples that is returned from get_links() 
   as an argument, and creates a list of just the names of each artist one time. 
   """
   artist_lst = []
   for result in data:
      if result[1] in artist_lst:
         continue
      else:
         artist_lst.append(result[1])
   return artist_lst


def createDatabase(db_name):
   """
   This function is the set up to create our database, Top100Songs.db
   """
   path = os.path.dirname(os.path.abspath(__file__))
   conn = sqlite3.connect(path+'/'+db_name)
   cur = conn.cursor()
   return cur, conn


def create_artist_table(artistnames):
   """
   This function takes in the list of all artistnames that is returned from 
   the get_artistnames function, and uses createDatabase to create a table in 
   the Top100Songs.db called artists, that assigns each artist name with an 
   artistid, in order to avoid repeating strings in our larger table.
   """
   cur, conn = createDatabase('Top100Songs.db')
   cur.execute("CREATE TABLE IF NOT EXISTS artists (aid INTEGER PRIMARY KEY, artistname STRING)")

   for i in range(len(artistnames)):
      #print(i)
      #print(artistnames[i])
      cur.execute("INSERT OR IGNORE INTO artists (aid, artistname) VALUES (?,?)",(i, artistnames[i]))
      conn.commit()




