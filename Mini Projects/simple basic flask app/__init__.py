from flask import Flask, render_template,request,jsonify
from flask_cors import CORS
from function import *
import json
import os

app = Flask(__name__)
cors = CORS(app)

#---------------------------- pages -------------------------------

@app.route('/login-page')
def login():
    return render_template("login.html")

@app.route('/profile-page')
def profile():
    return render_template("profile.html")


@app.route('/dashboard-page')
def dashboard():
    return render_template("dashboard.html")

@app.route('/profilefreeze-page')
def profilefreeze():
    return render_template("profilefreeze.html")

@app.route('/record-page')
def record():
    return render_template("dailyrecord.html")

@app.route('/createaccount-page')
def accountcreate():
    return render_template("createaccount.html")

@app.route('/graph-page')
def graph():
    return render_template("graph.html")

#-------------------- buttons -----------------------------------

@app.route('/login-button',methods = ["GET","POST"])
def login_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        login_button_data = login_button_function(data)
        return jsonify(login_button_data)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})

@app.route('/create-account-button',methods = ["GET","POST"])
def create_account_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        create_account_data = create_account_function(data)
        return jsonify(create_account_data)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})

@app.route('/profile-create-button',methods = ["GET","POST"])
def profile_create_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        profile_create_data = profile_create_function(data)
        return jsonify(profile_create_data)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})

@app.route('/profile-freeze-request',methods = ["GET","POST"])
def profile_freeze():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        profile_freeze_data = profile_freeze_function(data)
        return jsonify(profile_freeze_data)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})

@app.route('/record-create-button',methods = ["GET","POST"])
def record_create_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        record_create_data  =record_create_function(data)
        return jsonify(record_create_data)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})

@app.route('/dashboard-onscreen-load',methods = ["GET","POST"])
def dashboard_onscreen_load():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        dashboard_data = dashboard_function(data)
        return jsonify(dashboard_data)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})

@app.route('/graph-dataset-request',methods = ["GET","POST"])
def graph_dataset():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        dataset = graph_function(data)
        return jsonify(dataset)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"Status":False})



if __name__ == '__main__':
    app.run(debug=True,port=5001)