import mysql.connector
from datetime import datetime
        
def execute_query(query,return_value = True,description = False):

    return_dic={}
    try:
        mydb = mysql.connector.connect(host="localhost",user = "root",database="health_tracker_2")
        cursor = mydb.cursor()
        cursor.execute(query)
        
        if return_value == True:
            myresult = cursor.fetchall()
            return_dic["result"] = myresult
        
        if description == True:
            print('came for discription')
            description = cursor.description
            return_dic["description"] = description
        
        return_dic["Status"] = True
        mydb.commit()
        mydb.close()
        return return_dic
    except Exception as e:
        print("error: ",e)
        mydb.rollback()
        mydb.close()
        return {"Status":False}

def login_button_function(data):
    try:
        return_dic = {}
        useremail = data["UserEmail"]
        password = data["Password"]
        query = "SELECT IsProfileCreated,UserId FROM User WHERE UserEmail = '{}' AND UserPassword = '{}'".format(useremail,password)
        result = execute_query(query,True)
        if result["Status"] == True :
            print("login result :",result)
            if len(result['result']):
                return_dic['ValidLogin'] = True
                return_dic['IsProfileCreated'] = result['result'][0][0]
                return_dic['UserId'] = result['result'][0][1]
                return_dic['Status'] = True
            else:
                return_dic['ValidLogin'] = False
                return_dic['Status'] = True
        else:
            return_dic['Status'] = False
        
        return return_dic

    except Exception as e :
        print("login_button_function:Error is {}".format(str(e)))
        return {"Status": False}

def create_account_function(data):
    try:
        useremail = data["UserEmail"]
        password = data["Password"]
        conformedpassword = data["ConformedPassword"]
        datecreated = str(datetime.datetime.now()).split('.')[0]
        if (password == conformedpassword):
            query = '''INSERT INTO User(UserEmail,UserPassword,IsActive,DateCreated,IsProfileCreated)
                       VALUES('{}','{}','{}','{}','{}')'''.format(useremail,password,1,datecreated,0)
            result = execute_query(query,False)
            if result['Status'] == False :
                return result
            return {"Status": True}
        else:
            return {"Status":False}

    except Exception as e :
        print("profile_create_function:Error is {}".format(str(e)))
        return {"Status": False}

def profile_create_function(data):
    
    try:
        userid = int(data["UserId"])
        firstname = data["FirstName"]
        lastname = data["LastName"]
        glucoselevel = data["GlucoseLevel"]
        heartrate = data["HeartRate"]
        caloriesburnt = int(data["CaloriesBurnt"])
        timeofexercise = int(data["TimeOfExercise"])
        comments = data["Comments"]
        
        today = datetime.now()
        d1 = today.strftime("%d/%m/%Y %H:%M")
        query = '''INSERT INTO health_tracker_survey(FirstName,LastName,GlucoseLevel,HeartRate,CaloriesBurnt,TimeOfExercise,Comments,CreatedBy,DateCreated,DateModified) Values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}') '''.format(firstname,lastname,glucoselevel,heartrate,caloriesburnt,timeofexercise,comments,int(userid),d1,d1)
        print(query)
        result = execute_query(query,False)
        if result['Status'] == False:
            return result
        query = ''' UPDATE User SET IsProfileCreated = '{}' WHERE UserId = '{}' '''.format(1,int(userid))
        result = execute_query(query,False)
        if result['Status'] == False:
            return result
        
        print("Done")
        return {"Status": True}
    except Exception as e :
        print("profile_create_function:Error is {}".format(str(e)))
        return {"Status": False}

def profile_freeze_function(data):
    try:
        return_dic = {} 
        userid = data["UserId"]
        query = '''select * from health_tracker_survey where CreatedBy = '{}' '''.format(int(userid)) 
        result = execute_query(query,return_value = True,description = True)
        if result['Status'] == False :
            return result
        print('result is :',result)
        columns = [column[0] for column in result["description"]]
        return_dic = dict(zip(columns, result['result'][0]))
        return_dic['Status'] = True
        print('return_dic :   ',return_dic)
        return return_dic
    except Exception as e :
        print("profile_freeze_function: Error is {}".format(str(e)))
        return {"Status": False}

def blog_freeze_function():
    try:
        return_list = [] 
        query = '''select FirstName as 'Title', DateModified as 'Date',Comments as 'Info' from health_tracker_survey  ''' 
        result = execute_query(query,return_value = True,description = True)
        if result['Status'] == False :
            return result
        print('result is :',result)
        columns = [column[0] for column in result["description"]]
        for i in result['result']:
            d = dict(zip(columns, i))
            print("--------------------")
            print(d)
            
            d["Date"] = str(d["Date"])
            return_list.append(d)
        print('return_list :   ',return_list)
        return return_list
    except Exception as e :
        print("blog_freeze_function: Error is {}".format(str(e)))
        return {"Status": False}




