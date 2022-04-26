from aem import con
from matplotlib import colors
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
from top100songs import get_artistnames, create_artist_table

def make_request(song_lst): 
    """
    This function is where we get requests from the iTunes API. We used the 
    term and media parameters to request information about each song in the 
    top 100 songs of all time. We did this by using a list (the list of tuples
    returned from get_links()) as an argument that is passed into this function. 
    This function creates a list of tuples with the song title and genre for each song. 
    """
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
    """
    This function creates a table in our Top100Songs.db titled genres, using the list of tuples 
    that is returned from make_request, each new genre is appended to a list and then inserted into
    the genre table, while also being assigned a genreid. This creates a genre table with each genre 
    in there one with a unqiue id. 
    """
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
    """
    This function creates a list of tuples, one for each song that has all of the song's information,
    creating the song's rank with a count and creating the tuple with the song title, artistname, year released
    and rank. 
    """
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
    """
    This function creates the songdata table in our Top100Songs.db. It takes in what is returned 
    from all_data, which is a list of tuples, one for each song containing all of its information:
    song title, artistname, genre, year released, and rank. This function inserts 25 rows into the table 
    each time it is run. The artists table and genres table are used to add the ids for each of those
    columns as to avoid repeating strings.
    """
    cur, conn = createDatabase('Top100Songs.db')
    cur.execute('CREATE TABLE IF NOT EXISTS songdata(rank INTEGER PRIMARY KEY, songtitle STRING, year INTEGER, artistid INTEGER, genreid INTEGER)')
    cur.execute('SELECT MAX(rank) FROM songdata')
    maxid = cur.fetchone()[0]
    if maxid == None:
        maxid = 1
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


def most_pop_genre(): 
    """
    This function is our first calculation. It takes a count of each genre and calculates the 
    number of songs that are in each genre from the top100 songs of all time. 
    """
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
    """
    This function creates and writes our csv file titeled Test.csv, that writes out all the information we found 
    from our calculations as text. We created three different areas using two line breaks 
    to organize the data we collected from the calculations made. 
    """
    with open(file_name, 'w', newline="") as fileout:
        writer = csv.writer(fileout)
        header = ['Genre', 'Number of songs in Genre']
        writer.writerow(header)
        for item in genre_data:
            l = []
            l.append(item[1])
            l.append(item[0])
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


def viz_one(genredata):
    """
    This is the first visualization. A bar graph is created, comparing the number of songs in each genre
    with genre on the xaxis and number of songs on the yaxis.
    """
    count = []
    genre = []
    for item in genredata:
        count.append(item[0])
        genre.append(item[1])
    plt.bar(genre, count, color = 'purple')
    plt.xlabel("Genre")
    plt.ylabel("Quantity")
    plt.title("Number of songs Top 100 Songs per Genre")
    plt.show()


#--------------------------------------------------------------
def most_pop_year(): 
    """
    This function is our second calculation, which selects a count of how many songs that are
    in the top100 songs of all time were released in each year. 
    """
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
    """
    This is our second visualization, which creates a line plot displaying the relationship
    between the number of songs released per year that are in the top100 songs of all time. 
    """
    count = []
    year = []
    for item in yeardata:
        count.append(item[0])
        year.append(item[1])
    plt.plot(year,count)
    plt.title('Songs that made the Top 100 List by Release Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Songs')
    plt.show()

# --------------------------------------------------------------

def songs_per_artist():
    """
    This function is our third calculation. We counted how many songs each artist has in
    the top100 songs of all time.
    """
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



def viz_three(numsongs):
    """
    This is our third visualization. We used the calculation from songs_per_artist to create a 
    pie chart displaying the amount of artists that had 1 song, versus 2 songs, versus 3+ songs 
    in the top100 songs of all time. 
    """
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
    xlabs = ['1 song', '2 songs', '3 songs']
    counts = [artist_1, artist_2, artist_3]
    plt.pie(counts, labels = xlabs, colors = ['green', 'aquamarine', 'blue'])
    plt.axis('equal')
    plt.title('Frequencies of Artists with one, two, or 3 songs in the top 100')
    plt.show()

def viz_four():
    """
    This function is a fourth visualization. We surveyed 25 of our friends and 
    family members and showed them the list of songs in the top100 songs of all 
    time, and then created a list out of their responses. We then used this information
    to create a pie chart out of the data.  
    """
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
    colors_ = ['red', 'orange', 'pink', 'aquamarine', 'blue', 'purple', 'violet']
    plt.pie(counts, labels = label, colors = colors_)
    plt.axis('equal')
    plt.title('25 Responses for Favorite Song out of top 100 songs of all time')
    plt.show()

def main():
    """
    The main function is where all of our functions are run with the proper arguments
    in order for the file to run the way we need it to. 
    """
    song_lst = get_links()
    artistnames = get_artistnames(song_lst)
    create_artist_table(artistnames)
    genres = make_request(song_lst)
    create_grene_table(genres)
    data = all_data(song_lst, genres)
    create_songdata_table(data)

    genre_data = most_pop_genre()
    year_data = most_pop_year()
    artist_data = songs_per_artist()
    write_csv(genre_data, year_data, artist_data, 'Test.csv')
        #--------uncomment below for each plot-----------------
    # genredata = most_pop_genre()
    # viz_one(genredata)

    # yeardata = most_pop_year()
    # viz_two(yeardata)

    # songs = songs_per_artist()
    # viz_three(songs)

    # viz_four()

if __name__ == '__main__':
    main()





