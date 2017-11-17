from flask import Flask, request, render_template, session
app = Flask(__name__)
import pandas as pd
import numpy as np
import graphlab as gl
from pymongo import MongoClient
import time
from pprint import pprint
from flask import Flask
import recommender as rec
import info as info
from dispatcher import add_job
app.secret_key = 'datascience'

model = rec.Recommender()

#Post Data Request:
#@app.route("/")
@app.route('/')
@app.route('/index')
def index():
    session["user_id"]=None
    session["profile"]=None
    session["rated"]=None
    return render_template('home.html')

@app.route('/recs', methods=['GET'] )
def show_five():
    if session["user_id"] == None:
        user_id = request.args.get('user_id')
        session["user_id"]=user_id
    if session["profile"] == None:
        session["rated"], session["profile"] = model.get_rated(user_id)
    # page = 'The Fraud Seer predicts:\n {0}'
    # model = FraudModel("./fraud.pkl")
    preds = model.five_recs(session["user_id"])
    # risk = model.risk(pred)
    return render_template('recs.html',
                            pred = preds,
                            user_id = session["user_id"],
                            profile = session["profile"],
                            rated = session["rated"]
                            )



@app.route('/top100', methods=['GET'] )
def top100():
    user_id=session['user_id']
    #text = request.args[user_id]
    preds = model.display_top_100(user_id)
    return render_template('top100.html',
                            user_id = user_id,
                            pred = preds,
                            profile = session["profile"])

@app.route('/feedback', methods=['GET'] )
def feedback():
    user_id=session['user_id']
    yn=request.args.get('yn')
    session['ts']=time.time()
    ts = session['ts']
    profile=session['profile']
    info.feedback_base(yn, user_id, profile, ts)
    #helpful=request.form['helpful']
    return render_template('feedback.html')

@app.route('/thanks', methods=['POST'] )
def feedback_got():
    ts = session['ts']
    comment = request.form['comment']
    info.feedback_comment(ts, comment)
    return 'Thanks for the feedback!'

@app.route('/update', methods=['GET'])
def update_me():
    user_id=session['user_id']
    email=request.args.get('email')
    add_job('user_poke', [user_id])
    info.email_form(user_id, email, True)
    return "Thanks! We'll let you know when the model has updated!"

@app.route('/update_model', methods=['GET'])
def update_model():
    response=model.reload_model()
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)




