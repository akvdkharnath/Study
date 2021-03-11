class Student(): #outter class
    def __init__(self,rollnumber,name,sex,brand,ram,processor,usbports):
        self.rollnumber=rollnumber
        self.name=name
        self.sex=sex
        self.lap=self.Laptop(brand,ram,processor,usbports) #laptop object form Laptop class
    
    def show(self):
        print(self.rollnumber,self.name,self.sex)
        self.lap.show()    #calling show method of inner class from outer class
    
    class Laptop(): #inner class
        
        def __init__(self,brand,ram,processor,usbports):
            self.brand=brand
            self.ram=ram
            self.processor=processor
            self.usbports=usbports

        def show(self):
            print(self.brand,self.ram,self.processor,self.usbports)
        
s1=Student('150040053','harnath','M','HP','8',"AMD",'4')
s1.show()

# calling show method of inner class from outside of the class 
lap1=Student.Laptop('dell','16','intel','2')   # creating an object for Laptop class outside the class 
lap1.show()  # calling inner show method 