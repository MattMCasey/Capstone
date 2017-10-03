from pymongo import MongoClient
import time
from info import user_poke

client = MongoClient()
db = client['bgg']
jobs = db['jobs']

keys = {'user_poke' : user_poke}

def add_job(func, inputs):
    inputs = list(inputs)
    jobs.insert_one({'time':time.time(), 'func':func, 'inputs':inputs})

def execute_jobs():
    for job in jobs.find({}).sort([('time',-1)]):
        kwargs = ', '.join(job['inputs'])
        print job['func']
        keys[job['func']](kwargs)
        jobs.delete_one({'time':job['time']})

if __name__ == '__main__':
    while 1 == 1:
        execute_jobs()
        print 'Jobs completed at ', time.ctime()
        time.sleep(3600)
