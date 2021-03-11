class Computer:
    def __init__(self):  # for every object this method will assign same value
        self.ram='4gb'
        self.processor='i5'
        self.brand='Intel'
    
    def compare(self,other): #self is from object we are calling and other is the opject passed as peremeter 
        if self.ram==other.ram :
            return "both rams are equal"
        else :
            return "Both are with different rams"

c1=Computer()   #here Computer is called as constructor by calling constructor it it self call __init__ method 
c2=Computer()   # two objects c1,c2 with computer class are created 

c1.ram="8gb"    #here we are changing the ram value for the object c1
c2.processor="AMD"  #here we are changing the processor value for the object c2

# here c1 is passed as self and c2 is passed as other for the method
print(c1.compare(c2))

