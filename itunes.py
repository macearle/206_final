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
# from sqlalchemy import values
from top100songs import get_links
from top100songs import createDatabase
import re


def make_request(song_lst): 
    matches = []
    songs = []
    genres = []
    count = 0
    #-----------
    # reg_exp_feat = r"(^.*) Feat.*"
    # reg_exp_parenth = r"(^.*) \(.*"
    # for item in song_lst:
    #     full_song = item[0]
    #     if full_song[0] == '(':
    #         starts_with_p = r"\(.*\) (.*)"
    #         song = re.findall(starts_with_p,full_song)[0]
    #     elif ')' == full_song[-1]:
    #         song = re.findall(reg_exp_parenth,full_song)[0]
    #     else:
    #         song = full_song
    #     full_artist = item[1]
    #     if "Feat" in full_artist:
    #         artist = re.findall(reg_exp_feat,full_artist)[0]
    #     else:
    #         artist = full_artist
    #     year = item[2]
    #______________
    for item in song_lst:
        song = item[0]
        artist = item[1]
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
   cur.execute("CREATE TABLE IF NOT EXISTS genres (id INTEGER PRIMARY KEY, genre STRING)")
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
      cur.execute("INSERT OR IGNORE INTO genres (id, genre) VALUES (?,?)",(i, only_genre[i]))
      conn.commit()

def all_data(songinfo, genres):
    data = []
    rank = 1
    for songs in genres:
        song = songs[0]
        genre = songs[1]
        for item in songinfo:
            if song == item[0]:
                artistname = item[1]
                year = item[2]
        data.append((song, genre, artistname,year, rank))
        rank += 1
    return data

def create_songdata_table(alldata): 
    cur, conn = createDatabase('Top100Songs.db')
    cur.execute('CREATE TABLE IF NOT EXISTS songdata(rank INTEGER PRIMARY KEY, songtitle STRING, year INTEGER, artistid INTEGER, genreid INTEGER)')
    # start = 0
    cur.execute('SELECT MAX(rank) FROM songdata')
    maxid = cur.fetchone()[0]
    if maxid == None:
        maxid = 1
        print(maxid)
        print(type(maxid))
        print('--------------')
    try:
        for songs in alldata[maxid: maxid+25]:
                    song = songs[0]
                    genre_ = songs[1]
                    cur.execute("SELECT id FROM genres WHERE genre = ?", (genre_,))
                    gid = int(cur.fetchone()[0])
                    artistname = songs[2]
                    cur.execute("SELECT aid FROM artists WHERE artistname = ?", (artistname,))
                    id = int(cur.fetchone()[0])
                    year = songs[3]
                    rank = songs[4]
                    cur.execute('INSERT OR IGNORE INTO songdata(rank, songtitle, year, artistid, genreid) VALUES (?,?,?,?,?)', (rank, song, year, id, gid))
        conn.commit()
    except:
        for songs in alldata[maxid:]:
                    song = songs[0]
                    genre_ = songs[1]
                    cur.execute("SELECT id FROM genres WHERE genre = ?", (genre_,))
                    gid = int(cur.fetchone()[0])
                    artistname = songs[2]
                    cur.execute("SELECT aid FROM artists WHERE artistname = ?", (artistname,))
                    id = int(cur.fetchone()[0])
                    year = songs[3]
                    rank = songs[4]
                    cur.execute('INSERT OR IGNORE INTO songdata(rank, songtitle, year, artistid, genreid) VALUES (?,?,?,?,?)', (rank, song, year, id, gid))
        conn.commit()

    # else:
    # if maxid == 100:
    #     print('All songs added')
    
    # else:
    #     if maxid+25 >= 100:
    #         for songs in alldata[maxid:]:
    #             song = songs[0]
    #             genre_ = songs[1]
    #             cur.execute("SELECT id FROM genres WHERE genre = ?", (genre_,))
    #             gid = int(cur.fetchone()[0])
    #             artistname = songs[2]
    #             cur.execute("SELECT aid FROM artists WHERE artistname = ?", (artistname,))
    #             id = int(cur.fetchone()[0])
    #             year = songs[3]
    #             rank = songs[4]
    #             cur.execute('INSERT OR IGNORE INTO songdata(rank, songtitle, year, artistid, genreid) VALUES (?,?,?,?,?)', (rank, song, year, id, gid))
        # else:
        #     for songs in alldata[maxid: maxid+25]:
        #         song = songs[0]
        #         genre_ = songs[1]
        #         cur.execute("SELECT id FROM genres WHERE genre = ?", (genre_,))
        #         gid = int(cur.fetchone()[0])
        #         artistname = songs[2]
        #         cur.execute("SELECT aid FROM artists WHERE artistname = ?", (artistname,))
        #         id = int(cur.fetchone()[0])
        #         year = songs[3]
        #         rank = songs[4]
        #         cur.execute('INSERT OR IGNORE INTO songdata(rank, songtitle, year, artistid, genreid) VALUES (?,?,?,?,?)', (rank, song, year, id, gid))
    # conn.commit()
 

#select frequencies of genres 
def most_pop_genre(): 
    cur,conn = createDatabase('Top100Songs.db')
    cur.execute("""
    SELECT COUNT(*), genre
    FROM songdata
    JOIN genres
    ON genres.id = songdata.genreid
    GROUP BY genres.genre
    """)
    data = cur.fetchall()
    print(data)
    return data

def write_csv(genre_data, year_data, artist_data, file_name):
    with open(file_name, 'w', newline="") as fileout:
        writer = csv.writer(fileout)
        header = ['Genre', 'Number of songs in Genre']
        writer.writerow(header)
        for item in genre_data:
            l = []
            l.append(item[0])
            l.append(item[1])
            writer.writerow(l)
        writer.writerow([' '])
        writer.writerow(["Year", "Number of songs released in that year"])
        for item in year_data:
            l1 = []
            l1.append(item[1])
            l1.append(item[0])
            writer.writerow(l1)
        writer.writerow([' '])
        writer.writerow(["Artist Name", "Number of songs they have in top 100 songs of all time"])
        for item in artist_data:
            l2 = []
            l2.append(item[1])
            l2.append(item[0])
            writer.writerow(l2)


# Create a bar plot vizualization using matplotlib with the data returned from most_pop_genre
def viz_one(genredata):
    count = []
    genre = []
    for item in genredata:
        count.append(item[0])
        genre.append(item[1])
    plt.bar(genre, count, color = 'blue')
    plt.xlabel("Genre")
    plt.ylabel("Quantity")
    plt.title("Number of Top 100 Songs in Each Genre")
    plt.show()


#--------------------------------------------------------------
def most_pop_year(): 
    cur,conn = createDatabase('Top100Songs.db')
    cur.execute("""
    SELECT COUNT(*), year
    FROM songdata
    GROUP BY songdata.year
    """)
    data = cur.fetchall()
    return data



# Create a bar plot vizualization using matplotlib with the data returned from most_pop_year
def viz_two(yeardata):
    count = []
    year = []
    for item in yeardata:
        count.append(item[0])
        year.append(item[1])
    plt.plot(year,count)
    plt.title('Number of Songs in each Genre in the top 100 by year')
    plt.xlabel('Year')
    plt.ylabel('Number of Songs')
    plt.show()

# --------------------------------------------------------------

def songs_per_artist():
    cur,conn = createDatabase('Top100Songs.db')
    cur.execute("""
    SELECT COUNT(*), artistname
    FROM songdata
    JOIN artists
    ON artists.aid = songdata.artistid
    GROUP BY artists.artistname
    """)
    numsongs = cur.fetchall()
    return numsongs



def make_third_plot(numsongs):
    artist_1 = 0 
    artist_2 = 0
    artist_3 = 0 
    for song in numsongs:
        if song[0] == 1:
            artist_1 += 1
        elif song[0] == 2:
            artist_2 += 1
        else:
            artist_3 += 1
    # print(artist_1)
    # print(artist_2)
    # print(artist_3)
    xlabs = ['1', '2', '3']
    ylabs = [artist_1, artist_2, artist_3]
    plt.bar(xlabs, ylabs, color = "pink")
    plt.xlabel("Number of songs")
    plt.ylabel("Number of artists")
    plt.title("Frequency of artists with 1, 2, or 3+ songs in the top 100")
    plt.show()

def fav_songs():
    our_data = ["Uptown Funk!", "Shape of you", "I gotta feeling", "Hey Jude", "Uptown Funk!", 'Hey Jude', "Hey Jude", "Shape of you", "Shape of you", "Low", "Low", "I gotta feeling", "I gotta feeling", "Royals", "Royals", "Royals", "Royals", "Shape of you", "I gotta feeling", "I gotta feeling", "Low", "Low", "Uptown Funk!", "The Twist", "Shape of you"]
    responsedic = {}
    for response in our_data:
        if response in responsedic:
            responsedic[response] += 1
        else:
            responsedic[response] = 1
    #print(responsedic)
    label = list(responsedic.keys())
    counts = list(responsedic.values())
    plt.pie(counts, labels = label)
    plt.axis('equal')
    plt.title('25 Responses for Favorite Song out of top 100 songs of all time')
    plt.show()

def main():
    song_lst = get_links()
    print(song_lst)
    genres = make_request(song_lst)
    create_grene_table(genres)
    data = all_data(song_lst, genres)
    create_songdata_table(data)

    genre_data = most_pop_genre()
    year_data = most_pop_year()
    artist_data = songs_per_artist()
    write_csv(genre_data, year_data, artist_data, 'Test.csv')

if __name__ == '__main__':
    main()


#--------uncomment below for each plot-----------------
# genredata = most_pop_genre()
# viz_one(genredata)

# numsongs = songs_per_artist()
# make_third_plot(numsongs)

# yeardata = most_pop_year()
# viz_two(yeardata)

#fav_songs()

