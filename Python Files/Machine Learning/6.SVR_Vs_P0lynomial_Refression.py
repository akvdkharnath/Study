import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures,StandardScaler
from sklearn.linear_model import LinearRegression       
from sklearn.svm import SVR

dataset=pd.read_csv('Position_Salaries.csv')

X_Poly=dataset.iloc[:,1:2].values
Y_Poly=dataset.iloc[:,2].values

X_SVR=dataset.iloc[:,1:2].values
Y_SVR=dataset.iloc[:,2].values

# Polynomial Regression

Polynomial_Regression=PolynomialFeatures(degree=4)    
X_poly_fit=Polynomial_Regression.fit_transform(X_Poly)     

Linear_Regression=LinearRegression()
Linear_Regression.fit(X_poly_fit,Y_Poly)
z=Linear_Regression.predict(Polynomial_Regression.fit_transform(X_Poly))

q=Linear_Regression.predict(Polynomial_Regression.fit_transform([[6.5]]))
print(q)

# SVR NON-linear Regression

x_c=StandardScaler()
y_c=StandardScaler()

X_SVR_fit=x_c.fit_transform(X_SVR)
Y_SVR_fit=y_c.fit_transform(Y_SVR)

SVR_regressor=SVR(kernel='rbf')
SVR_regressor.fit(X_SVR_fit,Y_SVR_fit)

Y_pred=SVR_regressor.predict([[6.5]])    
print(Y_pred)

plt.figure(1)
plt.plot(X_SVR_fit,SVR_regressor.predict(X_SVR_fit))
plt.scatter(X_SVR_fit,Y_SVR_fit,color='red')

plt.title('salary Vs Rank')
plt.xlabel('Rank of person')
plt.ylabel('pay pack of person')
plt.scatter(X_Poly,Y_Poly,color='r')
plt.plot(X_Poly,z,color='blue')
plt.show()
