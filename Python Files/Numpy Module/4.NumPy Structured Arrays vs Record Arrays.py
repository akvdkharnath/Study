import numpy as np
# Structured Arrays :

# here we are creating a datatype consisting of all the perameters given below which are used in our ndimention arrays 
person_datatype_def=[('name','S6'),('age','i8'),('sex','S6'),('sal','f8'),('height','f8'),('weight','f8')]
#creating an ndimention arrays using the predefined datatype
# 2D array
array_2d=np.zeros((5,6),dtype=person_datatype_def)
print(array_2d)
array_2d[3][2]=('harnath',22,'m',2211,5.5,65)
print(array_2d)

# direct access is also possible
# direct math operations are also possible
# we can also access one key value inthe datatype

print(array_2d['name'])

#here we can use atribute other than index 
#it also has new data type callde numpy.record

