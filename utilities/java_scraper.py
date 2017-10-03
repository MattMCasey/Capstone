from pymongo import MongoClient
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import os


from pyvirtualdisplay import Display
display = Display(visible=0, size=(1920, 1080))
display.start()

client = MongoClient()
db = client['bgg']
lastupdate = db['lastupdate']
driver = webdriver.Firefox()
ratings = db['game_ratings']


def end_to_end():
    print 'starting end_to_end'
    for game_id in lastupdate.distinct('game_id'):
        update_game(game_id['game_id'])


def update_game(game_id):
    i = 1
    go = True
    driver.get('https://boardgamegeek.com/boardgame/'+str(game_id))
    base = driver.current_url
    block1= '/ratings?pageid='
    block2 = '&rated=1'
    last = lastupdate.find_one({'game_id':game_id})['last_update']
    print(game_id, last)

    while go:
        url = base+block1+str(i)+block2
        print(i)
        i += 1
        go = scrape_page(url, game_id, last)
        time.sleep(120)

    lastupdate.update_one({'game_id':game_id}, {'$set':{'last_update':time.ctime()}})


def scrape_page(url, game_id, last):

    crnt = time.ctime()
    go = True
    driver.get(url)

    ratings = driver.find_elements_by_class_name('rating')
    user_ids = driver.find_elements_by_class_name('comment-header-user')
    dts = driver.find_elements_by_class_name('comment-header-timestamp')


    for i in range(len(ids)):
        #if rtgs[i+2].text!='':
#         if 'Today' not in times[i] and 'Yesterday' not in times[i]:
#             crnt = datetime.strptime(times[i], '%b %d, %Y')
#             print(rtgs[i+2].text, game_id, ids[i].text, crnt, crnt<stop)
#         else:
        ratings.insert_one({
            'user_id' : user_ids[i],
            'game_id' : game_id,
            'rating' : ratings[i+2]
            })

    if datetime.strptime(crnt[-1], '%b %d, %Y') < last:
        go = False

    return go

def clean_duplicates():
    extra = ratings.aggregate(
    [
        {"$group": {
            "_id" : {"user_id":"$user_id",
            "game_id":"$game_id"}, "count": {"$sum" : 1}}},
        {"$sort": {"count" : -1} },
        {"$match": {"count" : { "$gte" : 2}} }
    ], allowDiskUse=True
    )

    for entry in extra:
        print(entry)
        end = entry['count']
        for i in range(0, end -1):
            ratings.delete_one({'user_id':entry['_id']['user_id'], 'game_id':entry['_id']['game_id']})

if __name__ == '__main__':
    print 'program started'
    while 1 == 1:
        end_to_end()
        clean_duplicates()
