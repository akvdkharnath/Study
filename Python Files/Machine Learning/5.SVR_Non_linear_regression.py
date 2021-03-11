import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVR  #used to svm model 
from sklearn.preprocessing import StandardScaler # used for scaling 

dataset=pd.read_csv('Position_Salaries.csv')
X=dataset.iloc[:,1:2].values #here in this case we wil have only one columens so its better to conver it from vector to matric
Y=dataset.iloc[:,2].values.reshape(-1, 1)

#scaling
x_c=StandardScaler()
y_c=StandardScaler()

X=x_c.fit_transform(X)
Y=y_c.fit_transform(Y)

# developing model with svm
regressor=SVR(kernel='rbf')
regressor.fit(X,Y)

#result
Y_pred=regressor.predict([[6.5]])    #pay pack for perticular range 
print(Y_pred)
#graph
plt.figure(1)
plt.plot(X,regressor.predict(X))
plt.scatter(X,Y,color='red')
plt.title('salary Vs Rank')
plt.xlabel('Rank of person')
plt.ylabel('pay pack of person')
plt.show()
