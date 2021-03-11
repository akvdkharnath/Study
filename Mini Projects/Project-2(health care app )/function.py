import mysql.connector
import datetime
  
def calculateAge(birthDate): 
    today = datetime.date.today() 
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
    return age 
      
def execute_query(query,return_value = True,description = False):

    return_dic={}
    try:
        # mydb = mysql.connector.connect(host="sql12.freemysqlhosting.net",user="sql12329633",passwd="76chTkYrBz",database="sql12329633" )
        # mydb = mysql.connector.connect(host="127.0.0.1",user = "root@localhost",database="health_tracker")
        mydb = mysql.connector.connect(host="localhost",user = "root",database="health_tracker")
        
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

def cal_bmi(height,weight):
    try:
        height = height/100  # converting cm to meaters 
        bmivalue = weight/(height*height)
        if bmivalue < 18.5:
            bmicategory = "Under Weight"
        elif bmivalue > 18.4 and bmivalue < 25 :
            bmicategory = "Normal Weight"
        elif bmivalue > 24.9 and bmivalue < 30 :
            bmicategory = "Over Weight"
        elif bmivalue > 29.9 and bmivalue < 35 :
            bmicategory = "Obesity (Stage-1)"
        elif bmivalue > 34.9 and bmivalue < 40 :
            bmicategory = "Obesity (Stage-2)"
        else:
            bmicategory = "Obesity (Stage-2)"
        return_dic = {}
        return_dic["bmivalue"] = bmivalue
        return_dic["bmicategory"] = bmicategory
        return_dic["Status"] = True 
        return return_dic

    except Exception as e :
        print("cal_bmi:Error is {}".format(str(e)))
        return {"Status": False}

def cal_weight_bmr(height,weight,bmicategory,sex,age):
    try:
        return_dic = {}
        dataset_male = {
            137:{'min':29,'max':35},
            140:{'min':31,'max':39},
            142:{'min':34,'max':41},
            145:{'min':36,'max':44},
            147:{'min':39,'max':47},
            150:{'min':40,'max':50},
            152:{'min':40,'max':53},
            155:{'min':46,'max':56},
            157:{'min':49,'max':59},
            160:{'min':50,'max':60},
            163:{'min':50,'max':65},
            165:{'min':56,'max':68},
            168:{'min':58,'max':70},
            170:{'min':60,'max':74},
            173:{'min':63,'max':71},
            175:{'min':65,'max':80},
            178:{'min':67,'max':83},
            180:{'min':60,'max':86},
            183:{'min':72,'max':89},
            }
        dataset_female = {
            137:{'min':29,'max':35},
            140:{'min':31,'max':38},
            142:{'min':33,'max':40},
            145:{'min':35,'max':43},
            147:{'min':37,'max':45},
            150:{'min':39,'max':48},
            152:{'min':41,'max':50},
            155:{'min':43,'max':53},
            157:{'min':45,'max':56},
            160:{'min':47,'max':58},
            163:{'min':49,'max':60},
            165:{'min':51,'max':63},
            168:{'min':53,'max':65},
            170:{'min':55,'max':68},
            173:{'min':57,'max':70},
            175:{'min':59,'max':73},
            178:{'min':61,'max':75},
            180:{'min':63,'max':78},
            183:{'min':65,'max':80},
            }
        if sex == 'Male':
            if height in dataset_male:
                maxweight = dataset_male[height]['max']
                minweight = dataset_male[height]['min']
            else:
                lst = list(dataset_male.keys())
                height = lst[min(range(len(lst)), key = lambda i: abs(lst[i]-height))]
                maxweight = dataset_male[height]['max']
                minweight = dataset_male[height]['min']
            BMR = (10*weight) + (6.25*height) - (5*age) + 5
        else: # female
            if height in dataset_female:
                maxweight = dataset_female[height]['max']
                minweight = dataset_female[height]['min']
            else:
                lst = list(dataset_female.keys())
                height = lst[min(range(len(lst)), key = lambda i: abs(lst[i]-height))]
                maxweight = dataset_female[height]['max']
                minweight = dataset_female[height]['min']
            BMR = (10*weight) + (6.25*height) - (5*age) - 161
        
        if bmicategory == "Normal Weight":
            return_dic['suggestedbmr'] = BMR
            return_dic['message'] = "You are all right pls maintain the same daily routine and diet "
        
        elif bmicategory == "Under Weight":
            needtogain = ((minweight+maxweight)*0.5)-weight
            timeinmounths = round(needtogain/0.8)
            return_dic['suggestedbmr'] = BMR+250
            return_dic['message'] ="Sorry to say you are in {} category please gain weight follow BMR readings so will be all right in {} months".format(bmicategory,timeinmounths)
        
        elif bmicategory == "Over Weight" or bmicategory == "Obesity (Stage-1)" or bmicategory == "Obesity (Stage-2)" or bmicategory == "Obesity (Stage-3)" :
            needtogain = ((minweight+maxweight)*0.5)-weight
            timeinmounths = round(needtogain/0.8)
            return_dic['suggestedbmr'] = BMR-250
            return_dic['message'] ="Sorry to say you are in {} category pls loose weight follow BMR readings so will be all right in {} months".format(bmicategory,timeinmounths)
        
        return_dic['maxweight'] = maxweight
        return_dic['minweight'] = minweight
        return_dic['bmr'] = BMR
        return_dic['Status'] = True
        return return_dic
    except Exception as e:
        print("error: ",e)
        return {"Status":False}

def login_button_function(data):
    try:
        return_dic = {}
        useremail = data["UserEmail"]
        password = data["Password"]
        # query = 'select * from User'
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
        return_dic = {}
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
        middlename = data["MiddleName"]
        lastname = data["LastName"]
        DOB = data["DateOfBirth"]
        height = float(data["Height"])
        weight = float(data["Weight"])
        sex = data["Sex"]
        age = int(calculateAge(datetime.date(1997, 2, 3))) 
        address = data["Address"]
        phonenumber = data["PhoneNumber"]
        result = cal_bmi(height,weight)
        print('2')
        print(result)
        if result["Status"] == False :
            return result
        print("result--",result)
        bmivalue = int(result["bmivalue"])
        bmicategory = result["bmicategory"]

        result = cal_weight_bmr(height,weight,bmicategory,sex,age)
        if result["Status"] == False :
            return result
        print("result--",result)
        minweight = int(result['minweight'])
        maxweight = int(result['maxweight'])
        bmr = result['bmr']
        suggestedbmr = result['suggestedbmr']
        message = result['message']
        
        query = ''' UPDATE PersonalProfile SET IsActive = '{}' WHERE UserId = '{}' '''.format(0,int(userid))
        result = execute_query(query,False)
        if result['Status'] == False:
            return result

        query = '''INSERT INTO PersonalProfile(UserId,FirstName,MiddleName,LastName,DateOfBirth,Height,Weight,Sex,Age,BMIValue,BMICategory,Address,PhoneNumber,MinWeight,MaxWeight,BMRValue,SuggestedBMRValue,Message,IsActive) Values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}') '''.format(int(userid),firstname,middlename,lastname,DOB,float(height),float(weight),sex,int(age),int(bmivalue),bmicategory,address,phonenumber,int(minweight),int(maxweight),float(bmr),float(suggestedbmr),message,1)
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
        query = '''select * from personalprofile where UserId = '{}' and IsActive = '{}' '''.format(int(userid),1) 
        result = execute_query(query,return_value = True,description = True)
        if result['Status'] == False :
            return result
        print('result is :',result)
        columns = [column[0] for column in result["description"]]
        return_dic = dict(zip(columns, result['result'][0]))
        return_dic['Status'] = True
        return_dic['DateOfBirth'] = str(return_dic['DateOfBirth'])
        print('return_dic :   ',return_dic)
        return return_dic
    except Exception as e :
        print("profile_freeze_function: Error is {}".format(str(e)))
        return {"Status": False}

def dashboard_function(data):
    try:
        return_dic = {}
        userid = data["UserId"]
        query = ''' select * from DashBoard where UserId = '{}' '''.format(int(userid))
        result = execute_query(query,return_value = True,description = True)
        if result['Status'] == False :
            return result
        print('result is :',result)
        results = []
        columns = [column[0] for column in result["description"]]
        for row in result["result"]:
            results.append(dict(zip(columns, row)))
        return_dic["Record"] = results
        return_dic["Status"] = True
        return return_dic

    except Exception as e :
        print("dashboard_function: Error is {}".format(str(e)))
        return {"Status": False}

def record_create_function(data):
    try:
        userid = data["UserId"]
        calorieinput = float(data["Cin"])
        calorieoutput = float(data["Cout"])
        date = data["SelectedDate"]
        finalvalue = calorieinput - calorieoutput
        datecreated = str(datetime.datetime.now()).split('.')[0]
        print("datecreated")
        print(datecreated)
        print(date)
        query = '''SELECT SuggestedBMRValue from personalprofile where UserId = '{}' '''.format(int(userid))
        result = execute_query(query,True)
        if result['Status'] == False :
            return result
        print('result is :',result)
        SuggestedBMRValue = float(result['result'][0][0])
        variation = SuggestedBMRValue - finalvalue
        query = '''INSERT INTO  dashboard(UserId,IdealBMRValue,CalorieInput,CalorieOutput,FinalCalorie,Variation,Date,IsActive,DateCreated) Values('{}','{}','{}','{}','{}','{}','{}','{}','{}') '''.format(int(userid),float(SuggestedBMRValue),float(calorieinput),float(calorieoutput),float(finalvalue),float(variation),date,1,datecreated)
        result = execute_query(query,False)
        return result
    
    except Exception as e:
        print("record_create_function: Error is {}".format(str(e)))
        return {"Status": False}


def graph_function(data):
    try:
        return_dic = {}
        userid = data["UserId"]
        
        results = []
        x = 10
        query = '''select Date AS label ,CalorieOutput AS y FROM dashboard WHERE UserId = '{}' and IsActive = '{}' '''.format(int(userid),1)
        result = execute_query(query,True,True)
        columns = [column[0] for column in result["description"]]
        for row in result["result"]:
            results.append(dict(zip(columns, row)))
        for entry in results:
            entry["label"] = str(entry["label"])
            entry["x"] = x
            x = x+10
        return_dic["loose"] = results
        
        results = []
        x = 10
        query = '''select Date AS label ,CalorieInput AS y FROM dashboard WHERE UserId = '{}' and IsActive = '{}' '''.format(int(userid),1)
        result = execute_query(query,True,True)
        columns = [column[0] for column in result["description"]]
        for row in result["result"]:
            results.append(dict(zip(columns, row)))
        for entry in results:
            entry["label"] = str(entry["label"])
            entry["x"] = x
            x = x+10
        return_dic["gain"] = results
        
        results = []
        x = 10
        query = '''select Date AS label ,FinalCalorie AS y FROM dashboard WHERE UserId = '{}' and IsActive = '{}' '''.format(int(userid),1)
        result = execute_query(query,True,True)
        columns = [column[0] for column in result["description"]]
        for row in result["result"]:
            results.append(dict(zip(columns, row)))
        for entry in results:
            entry["label"] = str(entry["label"])
            entry["x"] = x
            x = x+10
        return_dic["maintain"] = results

        results = []
        x = 10
        query = '''select Date AS label ,Variation AS y FROM dashboard WHERE UserId = '{}' and IsActive = '{}' '''.format(int(userid),1)
        result = execute_query(query,True,True)
        columns = [column[0] for column in result["description"]]
        for row in result["result"]:
            results.append(dict(zip(columns, row)))
        for entry in results:
            entry["label"] = str(entry["label"])
            entry["x"] = x
            x = x+10
        return_dic["endoftheday"] = results
        
        return_dic["Status"] = True
        return return_dic
    except Exception as e:
        print("graph_function: Error is {}".format(str(e)))
        return {"Status": False}