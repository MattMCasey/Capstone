import pandas as pd
import numpy as np
import graphlab as gl
from pymongo import MongoClient
import pymongo
import time
import requests
from pprint import pprint
from flask import Flask
from info import email_update

g_client = MongoClient()
g_db = g_client['bgg']
g_ratings = g_db['game_ratings']
contacts = g_db['contacts']

class Recommender(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['bgg']
        #table of ratings
        self.ratings = self.db['game_ratings']
        #table for game meta data
        self.meta = self.db['game_meta']
        self.users = self.db['users']
        self.game_set = self.build_set()
        self.rec = gl.load_model('flaskapp/model')

    def reload_model(self):
        self.rec = gl.load_model('flaskapp/model')
        return "reloaded"
        
    def build_set(self):
        game_set = []
        for row in self.meta.find({'lastpub':{'$gt':2010}, 'special':'n'}):
            game_set.append(row['game_id'])
        return game_set

    def get_rated(self, user_id):
        game_ids=[z['game_id'] for z in self.ratings.find({"user_id": user_id}).sort([("rating", pymongo.DESCENDING)]).limit(10)]
        #rated = set(self.users.find_one({'user_id':user_id})['filter'])
        profile = True
        rated=[]
        for entry in game_ids:
            full = self.meta.find_one({'game_id':entry})
            if full != None:
                rated.append(full['game_name'])
        if len(rated) == 0:
            profile = False
            
        return rated, profile
    
    def get_top_100(self, user_id):

        #building filter to prevent returning already-rated games
        #if self.users.find_one({'user_id':user_id}) == None or self.users.find_one({'user_id':user_id})['filter'] == []:
            #rated = []
            #for entry in self.ratings.find({"user_id": user_id}):
                #rated.append(entry['game_id'])
            #self.users.insert_one({'user_id':user_id, 'filter': rated })

        
        #rated=[z['game_id'] for z in self.ratings.find({"user_id": user_id})]
        #rated = set(self.users.find_one({'user_id':user_id})['filter'])
        #profile = True
        #if len(rated) == 0:
            #profile = False
        #unrated = self.game_set - rated

        #getting recommendations
        recs = self.rec.recommend(users=[user_id], items=self.game_set, k=100)
        preds = [x['game_id'] for x in recs]

        base_url = "https://www.amazon.com/gp/search?ie=UTF8&tag=clevermovegam-20\
&linkCode=ur2&linkId=a6842f74a11a112ea8cbc1c5f8470f00\
&camp=1789&creative=9325&index=toys-and-games&\
keywords="

        top_100_names =[]
        top_100_bgg =[]
        top_100_amazon = []
        top_100_images = []
        for entry in preds[:100]:
            full = self.meta.find_one({'game_id':entry})
            name = full['game_name']
            top_100_bgg.append('https://boardgamegeek.com/boardgame/' + entry)
            top_100_names.append(name)
            top_100_amazon.append(base_url+name)
            top_100_images.append(full['img'])

        return top_100_names, top_100_bgg, top_100_amazon, top_100_images


    def five_recs(self, user_id, start=0):
        #g1 = 1 #np.random.randint(0,5)
        #g2 = 2 #np.random.randint(5,15)
        #g3 = 3 #np.random.randint(15,35)
        #g4 = 4 #np.random.randint(35,60)
        #g5 = 5 #np.random.randint(60,100)

        gs = [x for x in range(start, start+5)]

        recs, bgg, amazon, img_path = self.get_top_100(user_id)

        final_n = []
        final_bgg = []
        final_amazon = []
        final_img = []

        for g in gs:
            final_n.append(recs[g])
            final_bgg.append(bgg[g])
            final_amazon.append(amazon[g])
            final_img.append(img_path[g])

        preds = zip(final_n, final_bgg, final_amazon, final_img)

        return preds


    def display_top_100(self, user_id):
        preds, bgg, amazon, img  = self.get_top_100(user_id)
        rank = [str(x) for x in range(1,101)]
        preds = zip(preds, bgg, amazon, rank)
        return preds


def build_model(num=11):
    print 'pulling records and building dataframe'
    df = pd.DataFrame(list(g_ratings.find()))
    df2 = df[['user_id', 'game_id', 'rating']]
    print 'cleaning dataframe'
    df2['rating'] = df2['rating'].convert_objects(convert_numeric=True)
    #sf = gl.SFrame.read_json('../mongo_exports/ratings.json', orient='records')
    sf = gl.SFrame(df2[['user_id', 'game_id', 'rating']])
    rec = gl.recommender.factorization_recommender.create(
            sf,
            user_id='user_id',
            item_id='game_id',
            target='rating',
            num_factors = num,
            solver='auto',
            verbose=True,
            side_data_factorization=False)
    rec.save('flaskapp/model')

if __name__ == '__main__':
    build_model()
    requests.get('http://localhost:8080/update_model')
    for record in contacts.find({'wants_update':True}):
        email_update(record['email'])
    contacts.update_many(
        {'wants_update':True},
        {'$set': {'wants_update':False}}
        )
