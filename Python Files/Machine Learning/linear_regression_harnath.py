import numpy as np 
import matplotlib.pyplot as plt 
 
def main():
	num_sum=0
	den_sum=0
	bill=np.array([34,108,64,88,99,51])
	tip=np.array([5,17,11,8,14,5])
	bill_mean=np.mean(bill)
	tip_mean=np.mean(tip)
	for i in range(len(bill)):
		num_sum +=(bill[i]-bill_mean)*(tip[i]-tip_mean)
		den_sum +=(bill[i]-bill_mean)*(bill[i]-bill_mean)
	b1=num_sum/den_sum 
	b0=tip_mean-b1*bill_mean
	print("b1 is "+str(b1))
	print("b0 is "+str(b0))
	plot_graph(bill,tip,b1,b0)

def plot_graph(bill,tip,b1,b0):
	plt.scatter(bill,tip,color="b",marker="x",s=30)
	tip_pred=b0+b1*bill
	plt.plot(bill,tip_pred,color="r")
	plt.xlabel("Bill")
	plt.ylabel("Tip")
	plt.title("Linear Regression")
	plt.show()
	



if __name__ == "__main__": 
    main()