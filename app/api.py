import flask
import jwt
import os
from utils import as_hours
from db import get_firestore
from time import time
from flask_cors import CORS,cross_origin

class BoardsCache:
    def __init__(self,boards=[],last_update=0) -> None:
        self.boards=boards
        self.last_update=last_update

class HistoryCache:
    def __init__(self) -> None:
        self.records={}
    def add_record(self,name,data) -> None:
        try:
            if as_hours(data["time"]) == as_hours(self.records[name]["time"]):
                self.records[name]["temperature"] = round(((self.records[name]["counter"] * self.records[name]["temperature"]) + data["temperature"]) / self.records[name]["counter"]+1,2)
                self.records[name]["humidity"] = round(((self.records[name]["counter"] * self.records[name]["humidity"]) + data["humidity"]) / self.records[name]["counter"]+1,2)
                self.records[name]["light"] = round(((self.records[name]["counter"] * self.records[name]["light"]) + data["light"]) / self.records[name]["counter"]+1,2)
                self.records[name]["time"] = as_hours(data["time"])
                self.records[name]["counter"]+=1
                return
            db.collection(u'{}'.format(name)) \
                .document(u'{}'.format(as_hours(self.records['time']))) \
                .set({
                    "temperature": self.records[name]["temperature"],
                    "humidity": self.records[name]["humidity"],
                    "light": self.records[name]["light"],
                    "counter": self.records[name]["counter"]
                })
            ###
            self.records[name]=data
            self.records[name]["counter"]=1
        except:
            self.records[name]={}
            self.records[name]["temperature"] = round(data["temperature"],2)
            self.records[name]["humidity"] = round(data["humidity"],2)
            self.records[name]["light"] = round(data["light"],2)
            self.records[name]["time"] = as_hours(data["time"])
            self.records[name]["counter"] = 1
            
            return
        
        

boardsCache=BoardsCache()
historyCache=HistoryCache()

def get_boards_list():
    return_list=[]

    if time()-600<boardsCache.last_update:
        return boardsCache.boards
    
    for board in db.collections():
        if board.id != 'accepted':
            return_list.append(board.id)

    boardsCache.boards=return_list
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
        
        historyCache.add_record(name,json_payload)
        app.logger.error(historyCache.records)
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

