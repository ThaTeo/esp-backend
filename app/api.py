import flask
import jwt
import os
from utils import as_hours
from db import get_firestore
from time import time
from flask_cors import CORS,cross_origin


def get_boards_list():
    return_list=[]
    for board in db.collections():
        if board.id != 'accepted':
            return_list.append(board.id)
    return return_list

db=get_firestore()

accepted=[doc.id for doc in db.collection(u'accepted').stream()]

app=flask.Flask(__name__)
CORS(app)

@app.route('/post/',methods=['POST'])
def post():
    
    json_payload = flask.request.json

    try:
        json_payload['humidity']/2
        json_payload['temperature']/2
        json_payload['light']/2
        json_payload['time']/2
    except:
        flask.abort(400)

    try:
        token = (flask.request.headers['Authorization']).split(' ')[1]
        name = jwt.decode(
        token,
        (os.environ['TOKEN_HEADER'] + str(json_payload['time']) + os.environ['TOKEN_TRAILER']),
        ['HS256'])['name']
    except:
        flask.abort(403)

    if name in accepted:

        db.collection(u'{}'.format(name)) \
            .document(u'current') \
            .set({
                'temperature': round(json_payload['temperature'],2),
                'humidity': round(json_payload['humidity'],2),
                'light': round(json_payload['light'],2),
                'time': json_payload['time']
            })
        reference=db.collection(u'{}'.format(name)) \
            .document(u'{}'.format(as_hours(json_payload['time']))) 
        
        doc=reference.get()

        if doc.exists:
            prev=doc.to_dict()
            reference.set({
                    'temperature':round((prev['temperature'] * prev['counter'] + json_payload['temperature']) / (prev['counter'] + 1), 2),
                    'humidity':round((prev['humidity'] * prev['counter'] + json_payload['humidity']) / (prev['counter'] + 1), 2),
                    'light':round((prev['light'] * prev['counter'] + json_payload['light']) / (prev['counter'] + 1), 2),
                    'counter':prev['counter'] + 1
                })
        else:
            reference.set({
                    'temperature': round(json_payload['temperature'],2),
                    'humidity': round(json_payload['humidity'],2),
                    'light': round(json_payload['light'],2),
                    'counter': 1
                })

        return {'success' : 'true'}
    flask.abort(403)

@app.route('/boards/',methods=['GET'])
@cross_origin()
def boards():
    return get_boards_list()

@app.route('/current/',methods=['GET'])
@cross_origin()
def current():
      
    return_list=[]

    for board in get_boards_list():
        return_list.append(
            {
                'name': board,
                'data': 
                    db.collection(u'{}'.format(board)) 
                        .document(u'current') 
                        .get().to_dict()
            }
        )

    return return_list

@app.route('/current/<name>',methods=['GET'])
@cross_origin()
def current_name(name):
    if name not in get_boards_list():
        flask.abort(404)
    return (
        {
            'name': name,
            'data': 
                db.collection(u'{}'.format(name)) 
                    .document(u'current') 
                    .get().to_dict()
        }
    )
        

@app.route('/history/',methods=['GET'])
@cross_origin()
def history():
    return_list=[]

    for board in get_boards_list():
        docs=[]
        now = as_hours(time())
        for doc in db.collection(u'{}'.format(board)).stream():

            if doc.id == 'current': 
                continue

            if doc.id <= str(now) and doc.id >= str(now - 10 * 60 * 60):
                docs.append({
                    'time': doc.id,
                    'data': doc.to_dict()
                })
        
        return_list.append({
            'name': board,
            'history': docs
        })

    return return_list

@app.route('/history/<name>',methods=['GET'])
@cross_origin()
def history_name(name):
    if name not in get_boards_list():
        flask.abort(404)

    docs=[]
    now = as_hours(time())
    for doc in db.collection(u'{}'.format(name)).stream():

        if doc.id == 'current': 
            continue

        if doc.id <= str(now) and doc.id >= str(now - 10 * 60 * 60):
            docs.append({
                'time': doc.id,
                'data': doc.to_dict()
            })
    return (
        {
            'name': name,
            'history': docs
        }
    )

