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

