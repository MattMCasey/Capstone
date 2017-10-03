from  pymongo import MongoClient
import requests
import time
from bs4 import BeautifulSoup


client = MongoClient()
db = client['bgg']
#table of ratings
ratings = db['game_ratings']
#table for game meta data
meta = db['game_meta']


def last_pub(game_id):
    newest = 0
    print(newest)
    url = 'https://www.boardgamegeek.com/xmlapi2/thing?id='+str(game_id)+'&versions=1'
    v_page = requests.get(url)
    v_souped = BeautifulSoup(v_page.content, 'html.parser')
    items = str(v_souped).split('</item>')
    for it in items:
        if 'English' in it:
            yr = it.split('yearpublished value="')[1]
            print(yr)
            nd = yr.index('"')
            if int(yr[:nd]) > newest:
                newest = int(yr[:nd])
    print(newest)
    meta.update_one({'game_id':game_id}, {'$set':{'lastpub':newest}})

def thumb_grab(game_id):
    url = 'https://www.boardgamegeek.com/xmlapi2/thing?id='+str(game_id)
    page = requests.get(url)
    souped = BeautifulSoup(page.content, 'html.parser')
    thumb = souped.select('image')

    if len(thumb) < 1:
        thumb = 'http://www.clevermovegames.com/wp-content/uploads/2013/08/lightbulbsquare.png'
    else:
        thumb = str(thumb)[8:-9]
    meta.update_one({'game_id':str(game_id)}, {'$set':{'img':thumb}})

def get_images():
    for game_id in meta.distinct('game_id'):
        print(game_id)
        if 'img' not in meta.find_one({'game_id':game_id}).keys():
            thumb_grab(game_id)
            time.sleep(4)
	if '>' in meta.find_one({'game_id':game_id})['img']: 
	    thumb_grab(game_id)
            time.sleep(4)
                    
def get_pubs():
    for game_id in meta.distinct('game_id'):
        if 'lastpub' not in meta.find_one({'game_id':game_id}).keys():
            last_pub(game_id)
	    time.sleep(4)
