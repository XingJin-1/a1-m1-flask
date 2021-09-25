import pytz
import json
import datetime
from datetime import datetime
from pprint import pprint
import os
import sys
import requests
from flask import Flask, jsonify, request, render_template, Response
from flask_mail import Mail, Message
from functools import wraps
import paho.mqtt.client as mqtt
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
import sqlite3
import logging
import redis
from rq import Queue, Worker, Connection
import time

r = redis.Redis()
q = Queue(connection=r)


app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensordata.db'

#Initialize database
db = SQLAlchemy(app)
db.init_app(app)
api = Api(app)



redis_client = redis.Redis(host="0.0.0.0",charset="utf-8",  decode_responses=True, port=6379, db=0)
redis_client1 = redis.Redis(host="0.0.0.0", charset="utf-8", decode_responses=True, port=6379, db=1)
redis_error = redis.Redis(host="0.0.0.0", charset="utf-8", decode_responses=True, port=6379, db=2)
redis_ccu = redis.Redis(host="0.0.0.0", charset ="utf-8", decode_responses=True, port=6379, db=3)


#for pub/sub
publisher = redis.Redis(host="0.0.0.0", charset="utf-8", decode_responses=True, port=6379, db=2)

subscriber = publisher.pubsub()
central_value = subscriber.subscribe("tp")

#Log to file
logging.basicConfig(filename="test.log", level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

#Create db model
class Datamodel(db.Model):
    __tablename__ = "sensordata"
    Target_Pos = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    Val_A_min = db.Column(db.Float, nullable=False)
    Val_A_max = db.Column(db.Float, nullable=False)
    Val_B_min = db.Column(db.Float, nullable=False)
    Val_B_max = db.Column(db.Float, nullable=False)

    def __init__(self, Target_Pos, Val_A_min, Val_A_max, Val_B_min, Val_B_max):
        Target_Pos = self.Target_Pos
        Val_A_min = self.Val_A_min
        Val_A_max = self.Val_A_max
        Val_B_min = self.Val_B_min
        Val_B_max = self.Val_B_max

    #Create a function to return a string after we added sth
    def __repr__(self):

        logging.debug(f"Position_Data: ('{self.Target_Pos}', '{self.Val_A_min}, '{self.Val_A_max}', '{self.Val_B_min}', '{self.Val_B_max}')")
        return f"Position_Data: ('{self.Target_Pos}', '{self.Val_A_min}, '{self.Val_A_max}', '{self.Val_B_min}', '{self.Val_B_max}')"

class Data(Resource):
    def get(self, pos):
        pos = Datamodel.query.filter_by(Target_Pos=pos).first()
        return render_template("data.html", pos=pos)

@app.route("/", methods=["GET"])
def start():
    return render_template("index.html")


ccu = ""


@app.route("/valueupdate", methods=['GET'])
def valueupdate():
   ccu = request.headers.get('Cpee-Callback')
   redis_ccu.lpush("ccu", ccu)
   return "", {'Content-Type': 'text/plain', 'CPEE-CALLBACK': 'true'}


@app.route("/value", methods=["GET"])
def value():
    entry = redis_client.get("Target Position")

    if (entry != None):
        pa = entry.split(":")
        value = {
            "Target Position": str(pa[0]),
            "Value A": float(pa[1]),
            "Value B": float(pa[2])
        }
        result = jsonify(value)
        logging.debug(value)
        return result, {'Content-Type': 'application/json; charset=utf-8'}

    else:
        value = { "Target Position": 0, "Value A": 0, "Value B": 0}
        result = jsonify(value)
        #log
        logging.debug(value)

        return result, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/valuelist")
def valuelist():
    return str(redis_client1.lrange("Target Position", 0, -1))

@app.route("/database", methods=["GET"])
def datadb():
    x = Datamodel.query.all()
    return str(x)

@app.route("/add", methods=['GET', 'POST'])
def add():
      #data = {"ADD": False}

      if request.method == 'POST':
        data = {}

        pa = request.form.get('Add')

        if pa == 'Yes':
          data = {"ADD": True}

        if pa == 'No':
          data = {"ADD": False}

        logging.debug(data)
        return data

      if request.method == 'GET':
        return render_template("button.html")


@app.route("/errordb", methods=['GET'])
def show_error():
    return str(redis_error.lrange("Error", 0, -1))



@app.route("/avgerror", methods=['GET'])
def avg_err():
   values = str(redis_error.lrange("Error", 0, -1))
   print(values)
   return "1"

@app.route("/createerror", methods=['GET', 'POST'])
def create_error():
    if request.method == 'POST':
        error_con = request.form['content']
        error_pos = request.form['error_pos']
        error_vala = request.form['error_vala']
        error_valb = request.form['error_valb']

        data = {
            "Content": error_con,
            "Error Position": error_pos,
            "Error Value A": error_vala,
            "Error Value B": error_valb,
        }
        inf = "Content: " + str(error_con) + ", Target Position: " + str(error_pos) + ", Value A: " + str(error_vala) + ", Value B: " + str(error_valb)
        redis_error.lpush("Error", inf)

        l = "Error" + str(inf)
        logging.debug(l)

        return data

    if request.method == 'GET':
        return render_template("createerror.html")

#ask user for Target_Pos, A and B value -> check if in range
@app.route("/check", methods=["GET", "POST"])
def ask_user():
    if request.method == "POST":

        tp = request.form.get("Target_Pos")
        va = request.form.get("ValA")
        vb = request.form.get("ValB")

        print(tp)
        print(va)
        print(vb)

        date = datetime.now()

        rangecheck = Datamodel.query.filter_by(Target_Pos=tp).first()
        if (rangecheck):
            if (float(va) > rangecheck.Val_A_min and float(va) < rangecheck.Val_A_max and float(vb) > rangecheck.Val_B_min and float(vb) < rangecheck.Val_B_max):
                response = {
                    "Valid": True,
                    "Tar_error": False,
                    "Val_error": False,
                    "Info": "Everything is fine",
                    "time": date
                    }
                logging.debug(response)
                return response

            else:

                if (float(va) < rangecheck.Val_A_min):
                    response = {"Valid": False,"Tar_error": False, "Val_error": True, "Info": "Problem: Value A to small", "time": date}
                    return response
                if(float(va) > rangecheck.Val_A_max):
                    response = {"Valid":False,"Tar_error": False, "Val_error": True, "Info": "Value A to big", "time": date}
                    return response
                if(float(vb) < rangecheck.Val_B_min):
                    response = {"Valid": False,"Tar_error": False, "Val_Error": True, "Info": "Value B to small", "time": date}
                    return response
                if(float(vb) > rangecheck.Val_B_max):
                    response ={"Valid": False,"Tar_error":False, "Val_error": True, "Info":  "Value B to big", "time": date}
                    return response
#            logging.debug(response)
#            return response
        else:
            response = {
                  "Valid": False,
                  "Tar_error": True,
                  "Val_error": False,
                  "Info": "Target Position not found",
                  "time": date
              }
            logging.debug(response)
            return response


    if request.method == "GET":
        return render_template("valuecheck.html")

@app.route("/create", methods=["GET", "POST"])
def create_pos():
    if (request.method == "POST"):

        tp = request.form["Target_Pos"]
        amin = request.form["Amin"]
        amax = request.form["Amax"]
        bmin = request.form["Bmin"]
        bmax = request.form["Bmax"]

        conn = sqlite3.connect("sensordata.db")
        c = conn.cursor()

        c.execute("INSERT INTO sensordata (Target_Pos, Val_A_min, Val_A_max, Val_B_min, Val_B_max) VALUES ( ?, ?, ?, ? , ?)",
                      (tp, amin, amax, bmin, bmax))
        conn.commit()
        msg = f"Sucessfully added Target Position: {tp}, Val_A_min: {amin}, Val_A_Max: {amax}, Val_B_min: {bmin}, Val_B_max: {bmax}"
        print(msg)
        c.close()
        conn.close()
        logging.debug(msg)
        result = {"Created": True, "Info": msg}
        return result
            #make adding to databse possible


    else:
        return render_template("createnewpos.html")



@app.route("/askdel", methods=["GET"])
def ask_delete():
     data = {"Delete": False}
     return jsonify(data)

@app.route("/askdel", methods=["GET"])
def ask_delete():
     data = {"Delete": False}
     return jsonify(data)



@app.route("/delete", methods=["GET", "POST"])
def delete_pos():
    if (request.method == "POST"):
        tp = request.form["Target_Pos"]
        conn = sqlite3.connect("sensordata.db")
        c = conn.cursor()
        c.execute("DELETE FROM sensordata WHERE Target_Pos= ?", (tp,))
        conn.commit()
        msg = f"Sucessfully deleted Target Position: {tp}"
        logging.debug(msg)
        return msg
    else:
        return render_template("delete.html")


api.add_resource(Data, "/Target_Pos/<string:pos>")

#Mail section
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "philip.mountainstreet@gmail.com"
app.config['MAIL_PASSWORD'] = "gdtfqesoozzqausy"
app.config["MAIL_DEFAULT_SENDER"] = "philip.mountainstreet@gmail.com"
app.config["MAIL_ASCII_ATTACHMENTS"] = False

mail = Mail(app)

def valuecases(tp, va, vb):
   conn = sqlite3.connect("sensordata.db")
   c = conn.cursor()
   c.execute("SELECT * FROM sensordata WHERE Target_Pos= ?", (tp,))
   data = c.fetchall()

   if(data == []):
     return {"Case": "position"}
   else:
     amin = float(data[0][1])
     amax = float(data[0][2])
     bmin = float(data[0][3])
     bmax = float(data[0][4])

     if( float(va) < (amin - 2) or float(va) > (amax + 2) or float(vb) < (bmin - 2) or float(vb) > (bmax + 2)):
        return {"Case": "critical"}

     else:
        return {"Case": "light"}

@app.route("/mail", methods=['GET', 'POST'])
def email():
  if (request.method == 'POST'):
   msg = ""

   tp = request.form['target_pos']
   va = request.form['vala']
   vb = request.form['valb']

   #cur_time = datetime.datetime.now(pytz.utc).isoformat()
   date = datetime.now()
   print(date)
   case = valuecases(tp, va, vb)
   ca = str(case['Case'])

   if(case['Case'] == "critical"):
     msg = Message("WARNUNG, SOFORT KORRIGIEREN !", recipients=["philip.mountainstreet@gmail.com"])


   if(case['Case'] == "light"):
     msg = Message("Warnung, Wertüberschreitung", recipients=["philip.mountainstreet@gmail.com"])

   if(case['Case'] == "position"):
     msg = Message("Warnung", recipients=["philip.mountainstreet@gmail.com"])
     msg.html = "Dies ist eine Warnemail, eine falsche Zielposition wird angefahren"
     err_info = {"Content": "position", "Target_Position": tp }
     str_err_inf = "Content: " + "position" ", Target_Position: " + str(tp)
     redis_error.lpush("Error", str_err_inf)
     redis_error.expire("Error", 259200)

     mail.send(msg)
     return {"send": True, "Case": ca, "time": date }


   conn = sqlite3.connect("sensordata.db")
   c = conn.cursor()
   c.execute("SELECT * FROM sensordata WHERE Target_Pos = ?", (tp,))
   data = c.fetchall()

   err_info = "Content: " + "value" + ", Case: " + ca + ", Target Position: " + str(tp) + ", Value A: " + str(va) + ", Value B: " + str(vb)

   redis_error.lpush("Error", err_info)
   redis_error.expire("Error", 259200)

   #adde msg.html
   msg.html = "Achtung Achtung"

   mail.send(msg)

   return { "send": True, "Case": ca, "time": date}


  if (request.method == 'GET'):
   return render_template("createerror.html")



#Mqtt section
client = mqtt.Client()

def getdegree(obj):
    value = float(obj) /291.267
    return round(value, 3)

def parsmsg(msg):
    pa = msg.payload.decode("utf-8")
    date = datetime.now()
    sp = pa.split(":")
    ls = len(sp) - 2
    Target_Pos = sp[ls]
    Val_A = getdegree(sp[ls-4])
    Val_B = getdegree(sp[ls - 3])

    v = str(Target_Pos) + ":" + str(Val_A) + ":" + str(Val_B)
    value = str(Target_Pos) + ":" + str(Val_A) + ":" + str(Val_B)

    if(Target_Pos != "P0"):
        payload = {"Target": Target_Pos, "x": Val_A, "y": Val_B}

        #payload = {"Target": Target_Pos, "x": Val_A, "y": Val_B, "time": date}
        ccus = redis_ccu.lrange("ccu", 0, -1)
        for item in ccus:
           ccu = item

           #r = requests.put(ccu, data=payload, headers= {"content-type":"application/json; charset=utf-8", "CPEE-UPDATE": "true"})
           r = requests.put(ccu, data=json.dumps(payload), headers={"content-type": "application/json; charset=utf-8","CPEE-UPDATE": "true"})

           if (r.status_code != requests.codes.ok):
              redis_ccu.lrem("ccu", 0, ccu)

        redis_client1.lpush("Target Position",str(v))
        redis_client1.expire("Target Position", 259200)

        redis_client.flushdb()

        publisher.publish("tp", value)
        redis_client.set("Target Position", value)



def onMessage(client, userdata, msg):
    print(msg.topic + ": " + msg.payload.decode())
    parsmsg(msg)

def onConnect(client, userdata, rc, msg):
    print("Connected ...")
    client.subscribe("/sensor")
    client.subscribe("/Target_Pos")

if __name__ == "__main__":
    client.on_message = onMessage
    client.on_connect = onConnect
    client.connect("cpee.org", 8080, 60)
    client.loop_start()
    app.run(host="::", port=4567, debug=True)