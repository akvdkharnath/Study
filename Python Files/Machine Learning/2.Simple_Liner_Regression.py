# Import block
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split    # used to split for train and test data
from sklearn.linear_model import LinearRegression       # used to do regression analysis

# Importing the data set
dataset=pd.read_csv('Salary_Data.csv')
X=dataset.iloc[:,:-1].values
Y=dataset.iloc[:,1].values

# Making the training and testing data set 
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=1/3,random_state=0) # x,y are input data test size is the persentage of the test data and always random_state will be zero

# Simple Linear Regression set
Linear_Regression=LinearRegression()
Linear_Regression.fit(X_train,Y_train)

# Results of the Prediction
Y_pred=Linear_Regression.predict(X_test)
print('real values are :')
print(Y_test)
print('generated values are :')
print(Y_pred)

# ploting the results for best analysis:

plt.figure(1)
plt.scatter(X_train,Y_train,color='red',label='Correct data')                                    # Perfect Answer
plt.scatter(X_train,Linear_Regression.predict(X_train),color='blue',label='Prediction data')     # Prediction Answer
plt.legend()

plt.title('Salary Vs Experience (Train data)(Simple Linear Regression)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')

# results for test data

plt.figure(2)
plt.scatter(X_test,Y_test,color='red',label='correct data')
plt.scatter(X_test,Linear_Regression.predict(X_test),color='blue',label='Prediction data')
plt.title('Salary Vs Experience(Testing Data)(Simple Linear Regression)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')

plt.show()