from flask import Flask, render_template,request,jsonify
from flask_cors import CORS
from function import *
import json
import os

app = Flask(__name__)
cors = CORS(app)

#---------------------------- pages -------------------------------

@app.route('/home-page')
def login():
    return render_template("home.html")

@app.route('/question-page')
def question():
    return render_template("question.html")

@app.route('/export-page')
def export():
    return render_template("export.html")



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
        return jsonify({"status":False})

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
        return jsonify({"status":False})

@app.route('/submit-survey-button',methods = ["GET","POST"])
def submit_survey_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        responce = submit_survey(data)
        return jsonify(responce)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"status":False})

@app.route('/create-question-button',methods = ["GET","POST"])
def create_question_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        responce = submit_question(data)
        return jsonify(responce)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"status":False})

@app.route('/submit-answer-button',methods = ["GET","POST"])
def submit_answer_button():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        responce = submit_answer(data)
        return jsonify(responce)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"status":False})

@app.route('/get-questions',methods = ["GET","POST"])
def get_questions():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        responce = get_qa(data)
        return jsonify(responce)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"status":False})


@app.route('/get-answers',methods = ["GET","POST"])
def get_answers():
    try:
        data=request.form
        data=data.to_dict()
        data = json.loads(data['file'])
        print("recived data is: {}".format(str(data)))
        responce = get_qa_answers()
        return jsonify(responce)
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"status":False})



if __name__ == '__main__':
    app.run(debug=True,port=5001)