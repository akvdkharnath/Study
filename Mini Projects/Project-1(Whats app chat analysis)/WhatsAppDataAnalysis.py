import os
import re
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import matplotlib.pyplot as plt
import json
# import plotly.plotly as py
# import plotly.graph_objs as go

# def analysis_date_Vs_chat(df):
# 	date_list=list(df['Date'].replace('251/2/1','1/1/01').replace('2015/2016/2017','1/1/01'))
# 	count_dup_date_list=[]
# 	for i in range(len(date_list)):
# 		date_list[i]=datetime.datetime.strptime(date_list[i], "%m/%d/%y").strftime("%d/%m/%y")

# 	print(date_list)
# 	#print(len(date_list))
# 	dup_date_list=list(set(date_list))
# 	#print(dup_date_list)
# 	for i in dup_date_list:
# 		count_dup_date_list.append(date_list.count(i))
# 	#print(count_dup_date_list)
# 	#print(max(count_dup_date_list))
# 	#print(count_dup_date_list.index(max(count_dup_date_list)))
# 	#print(dup_date_list[count_dup_date_list.index(max(count_dup_date_list))])
# 	print('number of days till now chated:'+str(len(dup_date_list)))
# 	plt.figure(1)
# 	plt.bar(count_dup_date_list,dup_date_list,color='blue')
# 	plt.show()

# def analysis_month_day_Vs_chat(df):
# 	date_list=list(df['Date'].replace('251/2/1','1/1/01').replace('2015/2016/2017','1/1/01'))
# 	month_list_count=[0,0,0,0,0,0,0,0,0,0,0,0]
# 	days30_list_count=[0]*31
# 	day30_name=list(range(1,32))
# 	month_name=['January','February','March','April','May','June','July','August','September','October','November','December']
# 	for i in range(len(date_list)):
# 		#converting date format to required one 
# 		date_list[i]=datetime.datetime.strptime(date_list[i], "%m/%d/%y").strftime("%d/%m/%y")
# 		#extracting month from the date
# 		temp=datetime.datetime.strptime(date_list[i], "%d/%m/%y").month  
# 		#adding the month to the month_list_count list
# 		month_list_count[temp-1]+=1
# 		#extracting day(30) from the date
# 		temp=datetime.datetime.strptime(date_list[i], "%d/%m/%y").day
# 		#adding the day(30) to the days30_list_count
# 		days30_list_count[temp-1]+=1
# 	plt.figure(2)
# 	plt.bar(month_name,month_list_count,color='blue')
# 	plt.title('Analysis_Month_Vs_Chat')
# 	plt.xlabel('Months')
# 	plt.ylabel('Number of Messages')
# 	plt.show()
    
# 	plt.figure(3)
# 	plt.bar(day30_name,days30_list_count,color='blue')
# 	plt.title('Analysis_Days_Vs_Chat')
# 	plt.xlabel('Days from 1 to 30')
# 	plt.ylabel('Number of Messages')
# 	plt.show()

# 	#print(month_list_count)

# def analysis_month_day_Vs_chat_with_out_chat(df):
# 	date_list=list(df['Date'].replace('251/2/1','1/1/01').replace('2015/2016/2017','1/1/01'))
# 	month_list_count=[0,0,0,0,0,0,0,0,0,0,0,0]
# 	days30_list_count=[0]*31
# 	day30_name=list(range(1,32))
# 	month_name=['January','February','March','April','May','June','July','August','September','October','November','December']
# 	for i in range(len(date_list)):
# 		#converting date format to required one 
# 		date_list[i]=datetime.datetime.strptime(date_list[i], "%m/%d/%y").strftime("%d/%m/%y")
# 		#extracting month from the date
# 		temp=datetime.datetime.strptime(date_list[i], "%d/%m/%y").month  
# 		#adding the month to the month_list_count list
# 		month_list_count[temp-1]+=1
# 		#extracting day(30) from the date
# 		temp=datetime.datetime.strptime(date_list[i], "%d/%m/%y").day
# 		#adding the day(30) to the days30_list_count
# 		days30_list_count[temp-1]+=1
# 	return [month_name,month_list_count,day30_name,days30_list_count]

# def time_Vs_chat(df):
# 	time_list_name=['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
# 	time_list_count=[0]*24
# 	result=[]
# 	time_list=list(df['Time'])
# 	for i in range(len(time_list)):
# 		str=time_list[i]
# 		temp=int(str[0:2])
# 		time_list_count[temp-1]+=1
# 	#print(time_list)
# 	plt.figure(4)
# 	plt.bar(time_list_name,time_list_count,color='blue')
# 	plt.title('Analysis_time_Vs_Chat')
# 	plt.xlabel('hours from 0 to 23')
# 	plt.ylabel('Number of Messages')
# 	plt.show()

# def ratio_of_chat(df):
# 	user_list=list(df['User'])
# 	user_list_count=[]
# 	dup_user_list=[' Harnath', ' Algonox Soujanya']
# 	#dup_user_list.remove('https')
# 	for i in range(len(dup_user_list)):
# 		user_list_count.append(user_list.count(user_list[i]))

# 	#print(dup_user_list)
# 	#print(user_list)
# 	#print(user_list_count)
# 	plt.figure(5)
# 	plt.pie(user_list_count,labels=dup_user_list)
# 	plt.show()

# 	df_user_1=df.loc[df['User']==dup_user_list[0]]
# 	df_user_2=df.loc[df['User']==dup_user_list[1]]
# 	user1_results=analysis_month_day_Vs_chat_with_out_chat(df_user_1)
# 	user2_results=analysis_month_day_Vs_chat_with_out_chat(df_user_2)
# 	bar_width = 0.35
# 	opacity = 0.8
	
# 	t1=go.Bar(x=user1_results[0],y=user1_results[1],name=dup_user_list[0])
# 	t2=go.Bar(x=user1_results[0],y=user1_results[1],name=dup_user_list[1])
# 	data=[t1,t2]
# 	layout = go.Layout(barmode='group')
# 	fig = go.Figure(data=data, layout=layout)
# 	py.iplot(fig, filename='grouped-bar')
	
# 	plt.figure(6)
# 	plt.bar(user1_results[2],user1_results[3],color='r',label=dup_user_list[0])
# 	plt.bar(user2_results[2],user2_results[3],color='g',label=dup_user_list[1])
# 	plt.legend()
# 	plt.title('Analysis_Days_Vs_Chat')
# 	plt.xlabel('Days from 1 to 30')
# 	plt.ylabel('Number of Messages')
# 	plt.show()

# 	print(df_user_1)
# 	print(df_user_2)


conf_file_path = str(os.getcwd())+'\\Config.json'

def get_file_path(conf_path):
	''' converts given json file into dictionary'''
	with open(conf_path, 'r') as fo:
		config_dict = json.loads(fo.read())
	return config_dict

def DataExtractionModule():
	try:

		config_dict = get_file_path(conf_file_path)
		InputFolder = config_dict["InputFolder"]
		OutputFolder = config_dict["DataFolder"]
		WhatsAppFileName = config_dict["FileName"]
		CsvFileName = WhatsAppFileName.split('.')[0] + '.csv'
		
		if os.path.exists(InputFolder+WhatsAppFileName):
			file_data = open(InputFolder+WhatsAppFileName,'r', encoding="utf8")
			WhatsApp_Content = file_data.read()
		else:
			return "File not found in location"
		
		#Get Date
		date_regex=re.compile(r'(\d+/\d+/\d+)')
		date=date_regex.findall(WhatsApp_Content)
		
		# Get time
		time_regex=re.compile(r'(24:00|2[0-3]:[0-5][0-9]|[0-1][0-9]:[0-5][0-9])')
		time=time_regex.findall(WhatsApp_Content)
		
		# Get Users
		user_regex=re.compile(r'-(.*?):')
		user=user_regex.findall(WhatsApp_Content)
		
		# Get Message
		message_regex=re.compile(r"(\n)(?<=)(\d+/\d+/\d+)(.*)")
		message=message_regex.findall(WhatsApp_Content)
		data=[]
		for w,x,y,z in zip(date,time,user,message):
			data.append([str(w),str(x),str(y),str(z)])
		
		# Create DataFrame from WhatsApp content
		df=pd.DataFrame(data,columns=("Date","Time","User","Message"))
		message_data=list(df['Message'])
		
		# Removing unwanted data from message
		for message in range(len(message_data)):
			message_data[message]=re.sub(r'.*:', ':',str(message_data[message])).replace(':','').replace('\')','')
		
		df=df.drop('Message',axis=1)
		
		# adding the modified message data
		
		df['Message']=np.array(message_data)
		print("date frame related to Chat: ")
		print(df)
		print('total number of messages till date are :'+str(df.shape[0]))
		#converting it to csv file
		
		df.to_csv(OutputFolder+CsvFileName)
		# analysis_date_Vs_chat(df)
		# #analysis_month_day_Vs_chat(df)
		# #time_Vs_chat(df)
		# ratio_of_chat(df)
		return ("Working Fine")
	except Exception as Error:
		return ("Error: {}".format(str(Error)))


if __name__=='__main__':
	result = DataExtractionModule()
	print(result)