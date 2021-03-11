import numpy as np 
import matplotlib.pyplot as plt
from pandas import DataFrame
import statsmodels.api as sm
import math

def main():
	Loan_Records={'credit_score':[655,692,681,663,688,693,699,699,683,698,655,703,704,745,702],'approved':[0,0,0,1,1,1,0,1,1,0,1,0,1,1,1]}
	df=DataFrame(Loan_Records,columns=['credit_score','approved'])
	print(df)
	plot_estimation(df)                 # step 1
	final_answer_statsmodels(df)        # step 2
	probability_graphs_up_to_now(df)    # step 3 

def plot_estimation(df):
	plt.figure(1)
	plt.scatter(df['credit_score'],df['approved'])
	plt.xlabel('credit_score')
	plt.ylabel('approved')
	plt.title('relation between credit_score and approved')
	plt.show()

def final_answer_statsmodels(df):
    X = df['credit_score']
    Y = df['approved']
    X = sm.add_constant(X) # adding a constant
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
    print_model = model.summary()
    print(print_model)

def probability_graphs_up_to_now(df):
	calculated_probabilities=[]
	for i in df['credit_score']:
		num=math.exp(-0.9610+(0.0023*i))
		den=1+num
		probability=num/den
		calculated_probabilities.append(probability)
	plt.figure(1)
	plt.scatter(df['credit_score'],calculated_probabilities)
	plt.xlabel('credit_score')
	plt.ylabel('calculated_probabilities')
	plt.title('final probability graph')
	plt.show()




if __name__=='__main__':
	main()