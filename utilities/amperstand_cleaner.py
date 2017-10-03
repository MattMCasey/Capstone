from pymongo import MongoClient

client = MongoClient()
db = client['bgg']
#table of ratings
ratings = db['game_ratings']
#table for game meta data
meta = db['game_meta']

for game in meta.find({'game_id':{'$exists': True}}, {'game_name':1, 'game_id':1, "_id":0}):
    if ';' in game['game_name']:
        name = game['game_name']
        stop = name.index('&')
        newname = name[:stop-1] + ' and ' + name[stop+6:]
        print(newname)
        meta.update({'game_id': game['game_id']}, {'$set' :{'game_name':newname}})
