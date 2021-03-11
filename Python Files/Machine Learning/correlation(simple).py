import math as m
import statistics 
import numpy as np
x=np.array([12,30,15,24,14,18,28,26,19,27])
y=np.array([20,60,27,50,21,30,61,54,32,57])
# mean for x and y
x_mean=statistics.mean(x)
y_mean=statistics.mean(y)
#coveriance for x,y 1 dimention
coveriance=np.cov(x,y)[0][1]     # here 0,1 represent that it is one dimention if not by default it will be 2 dimention 
# standed deviation for x and y
x_stdev=statistics.stdev(x)
y_stdev=statistics.stdev(y)
# correlation for it
correlation=coveriance/(x_stdev*y_stdev)
print("correlation is "+str(correlation))
