import numpy as np
#Slicing concept
a=np.array([1,2,3,4,5,6,7,8,9,0])  #this is also called as creating through list 
print(a)
# direct access is allowed
print(a[1])
print(a[2])
print(a[-1])
# different types of slicing in 1D
print(a[::2]) #print elements from first to last with whith making two elementsindex as one here 1,2 will be one which will print only 1,3,5,7 like this 
print(a[1:4])
print(a[-1:])
print(a[-4:-1])
print(a[1:-3])
a[2]=123
a[4]=a[2]+a[1]
print(a)
#%%
# in multidimenton array a[1][2] is equal to a[1,2]
# different types of slicing in 2D
b=np.arange(50).reshape(10,5)
print(b)
print(b[0:,0]) #this print the first col
print(b[4:7,:]) #print 4th to 7th row
print(b[4:7,2:]) #print 4row 2 col to 7row last col
print(b[::2,::2]) #make two rows and col as one


#%%
#boolean Mask array  or boolenan indexing

# this concept allow us to do direct action on the numpy arrays
subarray=0==(a%2) #boolen result of the condition 
print(subarray)
print(a[subarray])#values for the true conditions
#%%
#fancy indexing
#here we can make an n dimention array of our selected index values 
a=np.array([1,2,3,4,5,6,7,8,9,0])  #for 1D
index=[1,2,-5,-6]
print(a[index])
b=np.arange(50).reshape(10,5)
print(b[0:,[0,2,4]]) # for 2D here it take all rows and print only col with ndex 0,2,4

#%%
#problem:
c=np.arange(25).reshape(5,5)
sub=c%3==0
print(c[sub])
# or 
print(c[c%3==0])

#%%
#using if conditon for the concept of boolean mask array
print(np.where(c%3==0,c,0))  #f the condition is true then corrospiding a value is assignned if not zero will be assigned
create=np.empty_like(c)
print(create.fill(np.nan))
