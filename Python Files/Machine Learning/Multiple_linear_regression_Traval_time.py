import numpy as np 
import matplotlib.pyplot as plt
from pandas import DataFrame
from sklearn import linear_model
import statsmodels.api as sm

 
def main():
	trips_record={'miles_traveled':[89,66,78,111,44,77,80,66,109,76],'number_Deliveries':[4,1,3,6,1,3,3,2,5,3],'gasprice':[3.84,3.19,3.78,3.89,3.57,3.57,3.03,3.51,3.54,3.25],'travel_time':[7,5.4,6.6,7.4,4.8,6.4,7,5.6,7.3,6.4]}
	df=DataFrame(trips_record,columns=['miles_traveled','number_Deliveries','gasprice','travel_time'])
	print(df)
	plot_estimation(df)        # step 1
	#final_answer_sklearn(df)   # with sklearn        step 2
	#final_answer_statsmodels(df) # with statsmodels  step 2

def plot_estimation(df):
	# relation of Y1 and X1
	plt.figure(1)
	plt.scatter(df['miles_traveled'],df['travel_time'])
	plt.xlabel("miles_traveled")
	plt.ylabel("travel_time")
	plt.title("relation of miles_traveled and travel_time")
	# relation of Y1 and X2
	plt.figure(2)
	plt.scatter(df['number_Deliveries'],df['travel_time'])
	plt.xlabel("number_Deliveries")
	plt.ylabel("travel_time")
	plt.title("relation of number_Deliveries and travel_time")
	# relation of Y1 and X3
	plt.figure(3)
	plt.scatter(df['gasprice'],df['travel_time'])
	plt.xlabel("gasprice")
	plt.ylabel("travel_time")
	plt.title("relation of gasprice and travel_time")
	plt.show()
	
def final_answer_sklearn(df)(df):
	X = df[['miles_traveled','number_Deliveries']]
	Y = df['travel_time']
	# with sklearn
	regr = linear_model.LinearRegression()
	regr.fit(X, Y)
	print('Intercept: \n', regr.intercept_)
	print('Coefficients: \n', regr.coef_)

def final_answer_statsmodels(df):
    X = df[['miles_traveled','number_Deliveries']]
    Y = df['travel_time']
    X = sm.add_constant(X) # adding a constant
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
    print_model = model.summary()
    print(print_model)
	
if __name__ == "__main__": 
    main()
