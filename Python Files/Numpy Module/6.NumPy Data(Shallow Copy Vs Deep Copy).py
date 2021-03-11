import numpy as np
# it is of two types 1.shallo copy   2.deep copy
#shallo copy  copying two types of files in to one file 
# otheris to make dup copy of the file  

# reference equality
f1=np.array([1,2,3,4,5,6,7,8,9,0])
f2=f1   #f2 will also a numpy array which is a copy of f1
#but here the point is are they have same id are not to find ths use id
print(id(f1))
print(id(f2))
# here both id of f1 and f2 are same here both f1,f2 are said to be copy of that id

#value equality
#here in this case values may be equal but the id will not be equal
f3=np.array([1,2,3,4,5,6,7,8,9,0])
print(f1==f3)
print(id(f3))
print(id(f2))#here values will be equal but id will different  

#shallow copy
# concept of reference equality is also called as shallow copy
#here any value in f1 or f2 is changed it will also change the value n other file as there id are same

# deep copy
f4=np.copy(f1)
print(f1)
print(f4)
f1[2]=22 #f1[2] is changed it will not effect f4[2]
#here  values in f1,f4 will be same but the id will not same so any change in one file will not effect another file 