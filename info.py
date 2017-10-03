from pymongo import MongoClient
import time
from flask import Flask
import requests
from bs4 import BeautifulSoup

client = MongoClient()
db = client['bgg']
fback = db['feedback']
contacts = db['contacts']
ratings = db['game_ratings']


def feedback_base(helpful, user_id, profile, ts):
    fback.insert_one({'time': ts, 'user_id': user_id,
                          'profile' :profile, 'helpful':helpful})

def feedback_comment(ts, comment):
        fback.update_one({'time': ts},
                         {'$set':
                         {'comment' : comment}
                         })

def email_form(user_id, email,  wants_update=False):
    contacts.insert_one({
                         'user_id':user_id,
                         'email':email,
                         'wants_update':wants_update,
                         }
                         )

def email_update(email):
    print 'email_update updated ' + email
    return requests.post(
    "https://api.mailgun.net/v3/mail.clevermovegames.com/messages",
    auth=("api", "key-6951602764b3f8b2d19413a24b55e510"),
    data={"from": "CleverMoveGames.com <mailgun@mail.clevermovegames.com>",
    "to": email,
    "subject": "Your updated game suggestions",
    "text": "Hey there! \n \nPer your request, we have updated our board game  recommendation engine with new results based on your recent Board Game Geek ratings.\n \nGo to www.CleverMoveGames.com/board-game-recommender to see them."})

def page_grabber(url):
     get = requests.get(url)
     souped = BeautifulSoup(get.content, 'html.parser')
     return souped

def update_user(page, user_id):
    rtngs = page.find_all('rating')
    gms = page.find_all('item')

    for i in range(len(rtngs)):
        rating = str(rtngs[i])[15:20]
        end = rating.index('"')
        num = rating[:end]
        game = str(gms[i]).split('"')[3]
        ratings.update_one({'user_id':user_id, 'game_id':str(game)},
                           {'$set':
                            {'rating':num}},
                           upsert=True
                            )

def user_poke(user_id):
    url = 'http://boardgamegeek.com/xmlapi2/collection?username='+user_id+'&stats=1&rated=1'
    page = page_grabber(url)

    while 'Your request for this collection has been accepted' in str(page):
        time.sleep(5)
        page = page_grabber(url)


    update_user(page, user_id)

def feedback(user_id, helpful, comment=None):
    if comment==None:
        fback.insert_one({'time':time.ctime(), 'user_id' : user_id, 'helpful':helpful})
    else:
        fback.insert_one({'time':time.ctime(), 'user_id' : user_id, 'helpful':helpful, 'comment':comment})
