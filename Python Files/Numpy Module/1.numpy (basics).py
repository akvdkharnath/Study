import numpy as np
# creating an n-d array
# note: here n array every thing must be in same data type so if one is complex then it will change every thing to complex 
a=np.array([1,2,3])  #this is also called as creating through list 
print(a)
print("\n")
a=np.array([[1,2,3],[4,5,6],[7,8,9]]) #creating 2d arrays
print(a)
print(a.shape)     #print the structure of array in m(row)Xn(col) format


print(a.ndim)    #print the dimentions size mxn
print(a.size)   #print number of cells in the array
print(len(a)) #other way to find size
print(a.nbytes)   #print the memory neaded for the array
print(a.itemsize)
# return the array in the form of given data type
a=np.array([[1,2,3],[4,5,6],[7,8,9]],dtype=np.float64)
print(a)
a=np.array([[1,2,3],[4,5,6],[7,8,9]],dtype=complex)
print(a)

#giving the fixed values
a=np.arange(1,5)
print(a)
print("\n")
a=np.arange(1,10,2)  #it assign the value by a step size of 2
print(a)
print("\n")
a=np.ones((4,5))    #creates a 4x5 matrix of all 1
print(a)
print("\n")
a=np.zeros((4,5)) #creates a 4x5 matrix of all  0 
print(a)
print("\n")
a=np.linspace(1,20,40)
a=np.linspace(1,20,40,retstep=True) #this will also return the step size 
print(a)
print("\n")
a=np.arange(70)
a.shape=(5,14) #arrange the array in to 7x14 matrix 
print(a)
a=np.array([[1,2,3,4],[4,5,6,7],[7,8,9,0],[1,3,4,6]])
print(a.reshape(8,2))   #reshape rhe array into the given dimentions
print(a.reshape(1,16))
print(a.sum(axis=0))  #addition from top to buttom
print(a.sum(axis=1))   #addition from left to right
