import numpy as np
my_matrix=np.matrix([[1,2,3],[4,5,6],[7,8,9]])  #creating a matrix
print(my_matrix)
print(my_matrix.I)  #inverse 
print(my_matrix.T)  #transpose
print(np.eye(4))    #identical matrix which only take one peremaeter because its a squre matrix
#%%
#inbuilt function for solveing 3 equations problem used to find x,y,z
#which will have 3x3 matrix at left hand side and 3x1 on right hand side 
# this process will be more accurate then the step by step method
from numpy.linalg import solve
right_hand_matrix=([[1],[1],[3]])
print(solve(my_matrix,right_hand_matrix)) #solve take both the functions as input to solve the equations
#%%
# inbuilt functons for eigen values and eigen vectors
from numpy.linalg import eig
print(eig(my_matrix))
