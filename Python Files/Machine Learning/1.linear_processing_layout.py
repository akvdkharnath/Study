import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import Imputer        #for missing data
from sklearn.preprocessing import LabelEncoder,OneHotEncoder   #for encodeing the data from types to numbers,converts the binary data withe coloumns  
from sklearn.model_selection import train_test_split    # used to split for train and test data
from sklearn.preprocessing import StandardScaler   #this is for future scaling
dataset=pd.read_csv('Data.csv')
X=dataset.iloc[:,:-1].values
Y=dataset.iloc[:,3].values
#print(dataset)
#print(X)
#print(Y)

#missing data processing
imputer=Imputer(missing_values='NaN',strategy='mean',axis=0)  #missing data is the data which is in missing(which ew need to replace),strategy is the functon we are gong to use here,axis is on which axis we are going to work by default it is zero
imputer=imputer.fit(X[:,1:3]) #fit will generat a out put result and parameter is on which opereatrion need to be done here 1 and 2 coloumns so we passed 1:3
X[:,1:3]=imputer.transform(X[:,1:3]) #this fits the generated values in mssing location values passed in it are the coloumns need to processed
#print(X)

# Encoding the type data to value
# x value change
labelEncoder_X=LabelEncoder()   # used to encode the data
X[:,0]=labelEncoder_X.fit_transform(X[:,0])  # used to fit the generated values
onehotencoder=OneHotEncoder(categorical_features=[0])
X=onehotencoder.fit_transform(X).toarray()
# y value change
labelEncoder_Y=LabelEncoder()
Y=labelEncoder_Y.fit_transform(Y)  # used to fit the generated values here y whole data is in types so no need of slicing 
#print(X)
#print(Y)

#making the training and testing data set 
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.2,random_state=0) # x,y are input data test size is the persentage of the test data and always random_state will be zero

#Feature scaling
# in order to remove the problem of different scales 
sc_X=StandardScaler()
X_train=sc_X.fit_transform(X_train)    #coverting them to a single scale
X_test=sc_X.transform(X_test)          #here it is test data so no need of fitting 
  