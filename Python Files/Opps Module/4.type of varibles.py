# types of varibles :
#1. Class varibles
#2.Instance varibles

class Computer:
    usb_ports=4          # class varible
    def __init__(self):  # for every object this method will assign same value
        self.ram='4gb'       #instance varible
        self.processor='i5'  #instance varible
        self.brand='Intel'   #instance varible
    
    def compare(self,other): #self is from object we are calling and other is the opject passed as peremeter 
        if self.ram==other.ram :
            return "both rams are equal"
        else :
            return "Both are with different rams"

c1=Computer()   #here Computer is called as constructor by calling constructor it it self call __init__ method 
c2=Computer()   # two objects c1,c2 with computer class are created 

print(c1.ram,c1.processor,c1.usb_ports)
# or 
print(c1.ram,c1.processor,Computer.usb_ports)  # usb_ports refers to class so class name .varible is also fine 

# update a class varible 

Computer.usb_ports=8

