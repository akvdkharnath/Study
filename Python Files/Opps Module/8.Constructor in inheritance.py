
class A():         #parent class 
    def __init__(self):
        print(" init of A")
    def method1(self):
        print("method 1 of class A")
    
    def method2(self):
        print("method 2 of class A")

class B(A):       #single inheritance
    def method3(self):
        print("method 3 of class B")

    def method4(self):
        print("method 4 of class B")

a1=A()
# with this object a1 we can call all three methods of class A

b1=B()
# with this object b1 can call all methods of A and B 
