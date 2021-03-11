import mysql.connector
import datetime
      
mydb = mysql.connector.connect(host="localhost",user = "root",database="health_tracker_3")
cursor = mydb.cursor()

def login_button_function(data):
    try:
        return_dic = {}
        useremail = data["user_email"]
        password = data["password"]
        query = "SELECT Id,role FROM User WHERE user_email = %s AND password = %s"
        values = (useremail,password)
        cursor.execute(query,values)
        result = cursor.fetchall()
        if len(result):
            return_dic['login'] = True
            return_dic['user_id'] = result[0][0]
            return_dic['role'] = result[0][1]
            return_dic['status'] = True
            query = "SELECT QA.question,created_by,created_date from question_and_answer QA"
            cursor.execute(query)
            result = cursor.fetchall()
            temp_list = []
            for i in result:
                temp_dic = {}
                temp_dic["question"] = i[0]
                temp_dic["user_name"] = i[1]
                temp_dic["created_date"] = i[2]
                temp_list.append(temp_dic)
            return_dic['data'] = temp_list
        else:
            return_dic['login'] = False
            return_dic['status'] = True
        return return_dic
    except Exception as e :
        print("login_button_function:Error is {}".format(str(e)))
        return {"status": False}

def create_account_function(data):
    try:
        print("inside")
        username = data["user_name"]
        useremail = data["user_email"]
        password = data["password"]
        conformedpassword = data["conformed_password"]
        datecreated = str(datetime.datetime.now()).split('.')[0]
        if (password == conformedpassword):
            print('inner side')
            query = """INSERT INTO User(user_name,user_email,password,created_date) values(%s,%s,%s,%s)"""
            values = (username,useremail,password,datecreated)
            print(query)
            print(values)
            cursor.execute(query,values)
            mydb.commit()
            return {"status": True}
        else:
            print('wrong side')
            return {"status":False}
    except Exception as e :
        print("create_account_function:Error is {}".format(str(e)))
        return {"status": False}

def submit_survey(data):
    try:
        first_name = data["first_name"]
        last_name = data["last_name"]
        glucose_level = data["glucose_level"]
        heart_rate = data["heart_rate"]
        calories_burnt = data["calories_brunt"]
        time_of_exercise = data["time"]
        comments = data["comments"]
        query = "insert into survey(first_name,last_name,glucose_level,heart_rate,calories_burnt,time_of_exercise,comments) values(%s,%s,%s,%s,%s,%s,%s)"
        values = (first_name,last_name,glucose_level,heart_rate,calories_burnt,time_of_exercise,comments)
        cursor.execute(query,values)
        mydb.commit()
        return {"status": True}
    except Exception as e :
        print("submit_survey:Error is {}".format(str(e)))
        return {"status": False}

def submit_answer(data):
    try:
        # user_id = data["user_id"]
        # q_id = data["q_id"]
        answer = data["Data"]
        datecreated = str(datetime.datetime.now()).split('.')[0]
        for i in answer:
            question = i["Question"]
            answer = i["Answer"]
            if len(answer) != 0:
                query = "UPDATE question_and_answer set answer = %s,answered_date = %s,answered_by = 1,status = 1 where question = %s"
                values = (answer,datecreated,question)
                cursor.execute(query,values)
                mydb.commit()
        
        return {"status": True}
    except Exception as e :
        print("submit_answer:Error is {}".format(str(e)))
        return {"status": False}

def submit_question(data):
    try:
        user_id = data["user_id"]
        question = data["question"]
        datecreated = str(datetime.datetime.now()).split('.')[0]
        query = "INSERT into question_and_answer(created_by,created_date,question) values(%s,%s,%s)"
        values = (user_id,datecreated,question)
        cursor.execute(query,values)
        mydb.commit()
        return {"status": True}
    except Exception as e :
        print("submit_survey:Error is {}".format(str(e)))
        return {"status": False}

def get_qa(data):
    try:
        query = "SELECT QA.question,created_by,created_date from question_and_answer QA where status = 0"
        cursor.execute(query)
        result = cursor.fetchall()
        temp_list = []
        for i in result:
            temp_dic = {}
            temp_dic["question"] = i[0]
            temp_dic["user_name"] = i[1]
            temp_dic["created_date"] = str(i[2])
            temp_list.append(temp_dic)
        return temp_list
    except Exception as e :
        print("submit_survey:Error is {}".format(str(e)))
        return {"status": False}

def get_qa_answers():
    try:
        query = "SELECT QA.question,created_by,answered_by,created_date,answer from question_and_answer QA where status = 1"
        cursor.execute(query)
        result = cursor.fetchall()
        temp_list = []
        for i in result:
            temp_dic = {}
            temp_dic["question"] = i[0]
            temp_dic["user_name"] = i[1]
            temp_dic["answered_date"] = str(i[3])
            temp_dic["export_name"] = i[2]
            temp_dic["answer"] = i[4]

            temp_list.append(temp_dic)
        return temp_list
    except Exception as e :
        print("submit_survey:Error is {}".format(str(e)))
        return {"status": False}