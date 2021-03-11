# Types of methods :
# 1.Instance method avg
    # 1.1 accessors method   if we use only values of objects(get_object)
    # 1.2 Mutator method     if we update the value of an object (set_object)
# 2.Class method  which only use class objects refered with cls similarly like self
# 3.Static method  not refered with self and cls type objects 

class Student():

    school='algonox'                      #class varible 
    total_marks=100                       #class varible
    def __init__(self,m1,m2,m3):          # Instance method init  Accessors method
        self.m1=m1                        # instance varible 
        self.m2=m2                        # instance varible
        self.m3=m3                        # instance varible
    
    def average(self):                    # Instance method init  Accessors method here we are using instance varibles only but not updating them so it is called as accessors 
        return (self.m1+self.m2+self.m3)/3
    
    # get_object name is used to get the object value

    def get_m1(self):                     # Instance method init  Accessors method here we are using instance varibles only but not updating them so it is called as accessors
        return self.m1
    
    # get_object name is used to update the object value
    def set_m1(self,value):               # Instance method init  Mutator because here we are updating the object value
        self.m1=value

    #if we have n objects then there will be n number of set and get objects

    @classmethod                          # this decorator need to be used to sepator the instance methods from class methods  
    def getschool_name(cls):                 # Class method will use only class varibles here cls refers to student class how self works for methods 
        return cls.school

    @classmethod
    def gettotal_marks(cls):
        return cls.total_marks
    
    @staticmethod                         # this decorator need to be used to separate the static method from other methods 
    def sumitby5(value):                  # will not use any of the object it will just take a value and do some operations and will return the data
        return value+5


s1=Student(30,40,50)   #s1 object
s2=Student(60,70,80)   #s2 object

print(s2.average())
print(s1.get_m1())
s1.set_m1(40)
print(s1.get_m1())

print(Student.getschool_name())

print(Student.sumitby5(6))