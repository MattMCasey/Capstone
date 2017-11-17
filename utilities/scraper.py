from pymongo import MongoClient
import pprint
import requests
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import threading


client = MongoClient()
db = client['bgg']
#table of ratings
ratings = db['game_ratings']
#table for game meta data
meta = db['game_meta']

def get_meta(page, game_id):
    #print('get_meta')

    description = str(page.select('description')[0])[13:-14]
    min_players = str(page.select('minplayers'))[20:-16]
    max_players = str(page.select('maxplayers'))[20:-16]
    min_play_time = str(page.select('minplaytime'))[21:-17]
    max_play_time = str(page.select('maxplaytime'))[21:-17]
    year_published = str(page.select('yearpublished'))[23:-19]
    #this block gets us the static meta that we'll save

    page_text = str(page)
    #used for all loops that require a text split

    categories = []
    categories_raw = page_text.split('"boardgamecategory" value="')
    for i in range(1, len(categories_raw)):
        nd = categories_raw[i].index('"')
        categories.append(categories_raw[i][0:nd])

    mechanics = []
    mechanics_raw = page_text.split('"boardgamemechanic" value="')
    for i in range(1, len(mechanics_raw)):
        nd = mechanics_raw[i].index('"')
        mechanics.append(mechanics_raw[i][0:nd])
    #these two blocks get us categories & mechanics. A game can have > 1.

    game_name = page_text.split('type="primary" value="')
    nd = game_name[1].index('"')
    game_name = game_name[1][:nd]


    update = {'game_id': game_id,
              'game_name' : game_name,
              'description' : description,
              'min_players': min_players,
              'max_players' : max_players,
              'min_play_time' : min_play_time,
              'max_play_time' : max_play_time,
              'year_published' : year_published,
              'mechanics' : mechanics,
              'categories' : categories
             }

    if 'boardgameimplementation' in page_text:
        implementation_raw = page_text.split('boardgameimplementation" value="')
        nd = implementation_raw[1].index('"')
        implementation = implementation_raw[1][0:nd]
        update['implementation'] = implementation



    meta.insert_one(update)

    print(game_name)
    #inserts record into mongo database

#    return update

def get_ratings(page, game_id):
    #print('get_ratings')
    raw = str(page).split('rating="')
    top = len(raw)

    #print('top:', top)

    if top == 1:
        return False

    for i in range(1, top):
        #print(i)
        chopped = raw[i].split('"')
        rating = float(chopped[0])
        user_id = chopped[2]
        comment = chopped[4]

        update = {'user_id' : user_id,
                 'game_id' : game_id,
                 'rating' : rating}

        if len(comment) > 2:
            update['comment'] = comment

        ratings.insert_one(update)
        #ratings.update(update, update, upsert=True)

def scraping(game_id):
    base = 'https://www.boardgamegeek.com/xmlapi2/thing?id='

    game_id = str(game_id)
    #i = 0
    #start_raw = base + game_id + tail
    for i in range(1, 800):
        print(i, game_id)
        tail = '&ratingcomments=1&pagesize=100&page='+str(i)
        start_raw = base + game_id + tail

        raw = requests.get(base + game_id + tail)
        raw = BeautifulSoup(raw.content, 'html.parser')

        #get_ratings(raw, game_id)

        if i == 1:
            get_meta(raw, game_id)

        if get_ratings(raw, game_id) == False:
            return False

        time.sleep(5)

def t_scraping(game_id):
    base = 'https://www.boardgamegeek.com/xmlapi2/thing?id='

    game_id = str(game_id)
    #i = 0
    #start_raw = base + game_id + tail
    for i in range(1, 800):
        print(i, game_id)
        tail = '&ratingcomments=1&pagesize=100&page='+str(i)
        start_raw = base + game_id + tail

        raw = requests.get(base + game_id + tail)
        raw = BeautifulSoup(raw.content, 'html.parser')

        #get_ratings(raw, game_id)

        if i == 1:
            get_meta(raw, game_id)

        if get_ratings(raw, game_id) == False:
            return False

def central_controller(csv):
    table = pd.read_csv(csv, header=-1)
    array = list(table.iloc[:, 0])
    #return array
    for item in array:
        if scraping(item) == False:
            continue

# def threader(lst):
#     threads = []
#     for n in lst:
#         t = threading.Thread(target=scraping, args=(n,))
#         threads.append(t)
#         t.start()
#         time.sleep(5)
#
#     for x in threads:
#         x.join()

def threader(csv):
    table = pd.read_csv(csv, header=-1)
    array = list(table.iloc[:, 0])
    threads = []
    for n in array:
        t = threading.Thread(target=t_scraping, args=(n,))
        threads.append(t)
        t.start()
        time.sleep(5)

    for x in threads:
        x.join()


def one_meta(game_id):
    base = 'https://www.boardgamegeek.com/xmlapi2/thing?id='

    game_id = str(game_id)
    #i = 0
    #start_raw = base + game_id + tail

    print(game_id)
    tail = '&ratingcomments=1&pagesize=100&page=1'
    start_raw = base + game_id + tail

    raw = requests.get(base + game_id + tail)
    raw = BeautifulSoup(raw.content, 'html.parser')

    #get_ratings(raw, game_id)

    get_meta(raw, game_id)

    time.sleep(3)
