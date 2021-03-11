import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVR
# SVR will support both liner and non linear regression 


# import data set and extract the data required 
dataset=pd.read_csv('Position_Salaries.csv')
X=dataset.iloc[:,1:-1].values 
Y=dataset.iloc[:,3].values


regression = SVR