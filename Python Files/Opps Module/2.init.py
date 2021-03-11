class Computer: # defining a class with class keyword 
    def __init__(self,ram,processor):  # default method for the class 
        self.ram=ram                   # assigning objects
        self.processor=processor       # assigning objects

    def config(self): #def a method called config in opps terms functions are called as methods 
        print("Ram is {} and processor is {}".format(self.ram,self.processor))

# cerating a varible of class Computer
com1=Computer('4','i5')  #com1 is a varible of class Computer means com1 is af computer data type 
com2=Computer('8','i7')  #com2 is a varible of class Computer means com1 is af computer data type

# type-A
# Computer.config(com1)   # we are calling method config with com1 object 
# Computer.config(com2)   # we are calling method config with com2 object

# type-B(best approch)
com1.config()           # we are calling method config with com1 object 
com2.config()           # we are calling method config with com2 object

