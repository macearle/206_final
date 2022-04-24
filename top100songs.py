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


#grabs song title, artist name, year released for every song in top 100 songs of all time 
def get_links():
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
print(len(get_links()))

# gets a list of all the artists of the songs only once 
def get_artistnames(data):
   artist_lst = []
   for result in data:
      if result[1] in artist_lst:
         continue
      else:
         artist_lst.append(result[1])
   return artist_lst

# Creating database
def createDatabase(db_name):
   path = os.path.dirname(os.path.abspath(__file__))
   conn = sqlite3.connect(path+'/'+db_name)
   cur = conn.cursor()
   return cur, conn

#create table for artist and artistid
def create_artist_table(artistnames):
   cur, conn = createDatabase('Top100Songs.db')
   cur.execute("CREATE TABLE IF NOT EXISTS artists (artistid INTEGER PRIMARY KEY, artistname STRING)")

   for i in range(len(artistnames)):
      #print(i)
      #print(artistnames[i])
      cur.execute("INSERT OR IGNORE INTO artists (artistid, artistname) VALUES (?,?)",(i, artistnames[i]))
      conn.commit()

data = get_links()
artistnames = get_artistnames(data)
create_artist_table(artistnames)

# def main():
#    songinfo = get_links() 
#    artistnames = get_artistnames(songinfo)
#    create_artist_table(artistnames)
#    create_songdata_table(songinfo)


# main()