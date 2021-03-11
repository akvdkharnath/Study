import numpy as np
#%%
# Broadcasting Functionality
# rules are in scipy file
a=np.arange(16).reshape(2,8)
b=np.arange(16).reshape(8,2)
c=np.dot(a,b)
print(c)    # if these are of 1d matrics then it will work as linear operaton which is equal to np.inner








#%%
# difference between method and function 

d=np.arange(10)
print(np.sum(d)) #this is called function where data passed through it

print(d.sum())  #this is called the way of using it by varible type
#for access pls go through the screen shot 
print(b.sum(axis=0)) #access 0 in 2D is col so it print the sum of all elements in col wise
#%%
a=np.arange(16).reshape(2,8)
print(a.max())
print(a.argmax())