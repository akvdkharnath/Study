# mu=mean of sd
# sigma= for sd
import os
import numpy as np
import matplotlib.pyplot as plt  #used to create 2d plots in python
os.system('cls')  # used to clear the console cmd before running the code
#%%
# normal graphs

x=np.linspace(0,5,100)
# creating two graphs in same plot 
y=np.sin(4*x)*np.exp(-x)
z=np.cos(4*x)*np.exp(-x)
plt.figure()
plt.plot(x,y,'r--',label='plot for y') #here r is colour and -- used to indicade in dot line
plt.plot(x,z,'b',label='plot for z')
plt.title('my first plot')
plt.xlabel('x axis')
plt.ylabel('y axis')
plt.savefig('first_figure.png') #save a figure in png format
plt.legend()   #it is used to add label to the graph with out ths label will not show 


plt.figure()
plt.subplot(2,1,1)      #use of subplot
plt.plot(x,y,'r--',label='plot for y') #here r is colour and -- used to indicade in dot line
plt.subplot(2,1,2)
plt.plot(x,z,'b',label='plot for z')
plt.title('my first plot')
plt.xlabel('x axis')
plt.ylabel('y axis')
plt.savefig('first_figure.png') #save a figure in png format
plt.legend()   #it is used to add label to the graph with out ths label will not show 
#%%

# in histogram range is called as bins or buckets

# bar graphs

age_of_men=[12,13,15,34,54,65,78,34,67,99,78,12,33,5,77,56,32,88,95,65,87,80]
age_of_women=[92,3,35,84,84,45,58,94,37,89,38,2,3,15,57,86,42,98,45,65,37,10]
plt.figure()   # only for one perameter
plt.hist(age_of_men,bins=[1,20,50,100],rwidth=0.80,colour='b')
plt.xlabel('age range of men')
plt.ylabel('no of men')

plt.figure()   # for two or more perameter
plt.hist([age_of_men,age_of_women],bins=[1,20,50,100],rwidth=0.80,colour=['b','r'],label=['men','women'])
#  orientation='horizontal' or 'vertical' we can change the direction of the bar graph
plt.xlabel('age range of people')
plt.ylabel('no of persons')
plt.legend()
#%% 
# pie chart 

cost=[5000,2000,500,1000,300]
perpus=['food','room','net','transport','maintance']
plt.figure()
plt.axis('equal')   #this is added then output will be n circle if not oval
plt.pie(cost,labels=perpus,radius=1.5,autopct='%f%%')
#autopct is used to print the data on circle here %f%% will display data in the form of flot if it is %0.2f%% then it will show only two points next to decimal 
plt.pie(cost,labels=perpus,radius=1.5,autopct='%0.1f%%',explode=[0.1,0,0,0,0.5],startangle=45)
# explode will help us to get the pice of pie out of circle here we have five parts so 5 values in list if it is zero then no movememt if it is 0.1 it move a bit back   
# start angle is used to starting angle reference if it is 33 then it start ploting from 33 degree
plt.show()
