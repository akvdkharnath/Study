import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.tree import DecisionTreeRegressor
# data uploading
dataset=pd.read_csv('Position_Salaries.csv')
X=dataset.iloc[:,1:2].values
Y=dataset.iloc[:,2:3].values

#creating a model of Decision tree
regressor=DecisionTreeRegressor(random_state=0)
regressor.fit(X,Y)

#results
print(regressor.predict([[6.5]]))
 
#ploting the results 
plt.figure(1)
plt.scatter(X,Y,color='red')
plt.plot(X,regressor.predict(X),color='blue')
plt.xlabel('position')
plt.ylabel('salary')
plt.title('position Vs salary')
plt.show()