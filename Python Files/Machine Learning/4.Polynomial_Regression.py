# Import block
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures 
from sklearn.linear_model import LinearRegression       # used to do regression analysis

# Importing the data set
dataset=pd.read_csv('Position_Salaries.csv')
X=dataset.iloc[:,1:2].values #here in this case we wil have only one columens so its better to conver it from vector to matric
Y=dataset.iloc[:,2].values

#print(dataset)
#print(X)
#print(Y)

#model for polynomial Regression
Polynomial_Regression=PolynomialFeatures(degree=4)   #by defalult aslo it is 2 change the degree as u get the perfect curve at the end 
X_poly=Polynomial_Regression.fit_transform(X)      #converts the linear into polynomial type
# here we tranform the liner to polynomial type and from here we need to apply linear regression only   
Linear_Regression=LinearRegression()
Linear_Regression.fit(X_poly,Y)
z=Linear_Regression.predict(Polynomial_Regression.fit_transform(X))

#plot
plt.figure(1)
plt.scatter(X,Y,color='r')
plt.plot(X,z,color='blue')
plt.xlabel('Position_level')
plt.ylabel('Salary')
plt.show()

# for new values 
q=lin_reg.predict(poly_reg.fit_transform([[6.5]]))
print(q)
