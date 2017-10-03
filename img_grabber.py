import io
from PIL import Image
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import time

client = MongoClient()
db = client['bgg']
#table of ratings
ratings = db['game_ratings']
#table for game meta data
meta = db['game_meta']

def mass_scrape():
    ids = []
    with open('../ids.txt') as txt:
        for line in txt:
	    ids.append(line)
    for game_id in ids:
	print(game_id)
	get_images(game_id)
	time.sleep(2)

def get_images(game_id):
    base_url = 'https://boardgamegeek.com/boardgame/'
    page_url = base_url + str(game_id)
    wpage = requests.get(page_url)
    soup = BeautifulSoup(wpage.content, 'html.parser')
    img_url = str(soup).split('" property="og:image">')[0].split('"')[-1]

    r = requests.get(img_url)

    r.raise_for_status()
    with io.BytesIO(r.content) as f:
        with Image.open(f) as img:
            img.save('./static/'+str(game_id)+'.jpg')
