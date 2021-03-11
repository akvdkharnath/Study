# Import block
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder,OneHotEncoder   #for encodeing the data from types to numbers,converts the binary data withe coloumns  
from sklearn.model_selection import train_test_split    # used to split for train and test data
from sklearn.linear_model import LinearRegression       # used to do regression analysis

# Importing the data set
dataset=pd.read_csv('50_Startups.csv')
X=dataset.iloc[:,:-1].values
Y=dataset.iloc[:,4].values 

# Encoding the type data to value
labelEncoder_X=LabelEncoder()   # used to encode the data
X[:,3]=labelEncoder_X.fit_transform(X[:,3])  # used to fit the generated values
onehotencoder=OneHotEncoder(categorical_features=[3])
X=onehotencoder.fit_transform(X).toarray()

# Removing dummy varibles 
X=X[:,1:]
#print(X)

# Making the training and testing data set 
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.2,random_state=0) # x,y are input data test size is the persentage of the test data and always random_state will be zero

# Multiple Linear Regression 
Multiple_regressor=LinearRegression()
Multiple_regressor.fit(X_train,Y_train)
acc = Multiple_regressor.score(X_test, Y_test)
print('acc is {}'.format(acc))
# Result
Y_pred=Multiple_regressor.predict(X_test)
print('real values are :')
print(Y_test)
print('generated values are :')

# print(Y_pred)
# print(X_test)
# print(list(X.columns))
# print(list(dataset.columns))
# X_test_rotated=list(map(list, zip(*X_test)))

# ploting the results for best analysis:

# plt.figure(1)
# plt.scatter(X_train,Y_train,colour='red',label='correct data')
# plt.scatter(X_train,Multiple_regressor.predict(X_train),colour='blue',label='Prediction data')
# plt.title("Multiple Regressor")
# plt.legend()
# plt.show()