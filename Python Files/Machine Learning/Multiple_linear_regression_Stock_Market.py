import numpy as np 
import matplotlib.pyplot as plt
from pandas import DataFrame
from sklearn import linear_model
import statsmodels.api as sm

 
def main():
	Stock_Market = {'Year': [2017,2017,2017,2017,2017,2017,2017,2017,2017,2017,2017,2017,2016,2016,2016,2016,2016,2016,2016,2016,2016,2016,2016,2016],'Month': [12, 11,10,9,8,7,6,5,4,3,2,1,12,11,10,9,8,7,6,5,4,3,2,1],'Interest_Rate': [2.75,2.5,2.5,2.5,2.5,2.5,2.5,2.25,2.25,2.25,2,2,2,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75],'Unemployment_Rate': [5.3,5.3,5.3,5.3,5.4,5.6,5.5,5.5,5.5,5.6,5.7,5.9,6,5.9,5.8,6.1,6.2,6.1,6.1,6.1,5.9,6.2,6.2,6.1],'Stock_Index_Price': [1464,1394,1357,1293,1256,1254,1234,1195,1159,1167,1130,1075,1047,965,943,958,971,949,884,866,876,822,704,719]}
	df = DataFrame(Stock_Market,columns=['Year','Month','Interest_Rate','Unemployment_Rate','Stock_Index_Price'])
	print(df)
	#plot_estimation(df)        # step 1
	# final_answer_sklearn(df)   # with sklearn        step 2
	final_answer_statsmodels(df) # with statsmodels  step 2

def plot_estimation(df):
	# relation of Y1 and X1
	plt.figure(1)
	plt.scatter(df['Year'],df['Stock_Index_Price'])
	plt.xlabel("Year")
	plt.ylabel("Stock_Index_Price")
	plt.title("relation of Year and Stock_Index_Price")
	# relation of Y1 and X2
	plt.figure(2)
	plt.scatter(df['Month'],df['Stock_Index_Price'])
	plt.xlabel("Month")
	plt.ylabel("Stock_Index_Price")
	plt.title("relation of Month and Stock_Index_Price")
	# relation of Y1 and X3
	plt.figure(3)
	plt.scatter(df['Interest_Rate'],df['Stock_Index_Price'])
	plt.xlabel("Interest_Rate")
	plt.ylabel("Stock_Index_Price")
	plt.title("relation of Interest_Rate and Stock_Index_Price")
	# relation of Y1 and X4
	plt.figure(4)
	plt.scatter(df['Unemployment_Rate'],df['Stock_Index_Price'])
	plt.xlabel("Unemployment_Rate")
	plt.ylabel("Stock_Index_Price")
	plt.title("relation of Unemployment_Rate and Stock_Index_Price")
	
	plt.show()

def final_answer_sklearn(df):
	X = df[['Interest_Rate','Unemployment_Rate']]
	Y = df['Stock_Index_Price']
	# with sklearn
	regr = linear_model.LinearRegression()
	regr.fit(X, Y)
	print('Intercept: \n', regr.intercept_)
	print('Coefficients: \n', regr.coef_)
	
def final_answer_statsmodels(df):
    X = df[['Interest_Rate','Unemployment_Rate']]
    Y = df['Stock_Index_Price']
    X = sm.add_constant(X) # adding a constant
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
    print_model = model.summary()
    print(print_model)



if __name__ == "__main__": 
    main()
