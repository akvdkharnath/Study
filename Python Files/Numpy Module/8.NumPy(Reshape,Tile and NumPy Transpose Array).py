import numpy as np
array=np.arange(24)
array_2d=np.arange(24).reshape((2,12))
print(array_2d)
array_3d=np.arange(24).reshape((2,4,3))
print(array_3d)

#%%
# fliping:
print(np.fliplr(array_2d))
# flip the array left to right if it is 2d array
print(np.fliplr(array_3d))
#flip the array from top to down if it is 3d array

print(np.flipud(array_2d))
#flip the array from top to down if it is 2d array
print(np.flipud(array_3d))
#flip the array left to right if it is 3d array 
#%%
# roll:
print(np.roll(array,5))
print(np.roll(array,-5))
# if the value is +ve then left shift -ve right shft
#%%
# rotate:
#only applied for 2d arrays
print(np.rot90(array_2d)) #rotate anti clock wise direction
print(np.rot90(array_2d,k=-1)) # clock wise
#%%
# transpose:
# for 1d there will be no transpose 
print(np.transpose(array_2d))
print(np.transpose(array_3d,axes=(0,2,1)))
# here due to axes only 2 and 1 are re placed 