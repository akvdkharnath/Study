# Types of inheritance:
# 1.single inheritance
# 2.multi  inheritance
# 3.mutiple inheritance 

class A():         #parent class 
    def method1(self):
        print("method 1 of class A")
    
    def method2(self):
        print("method 2 of class A")

class B(A):       #single inheritance
    def method3(self):
        print("method 3 of class B")

    def method4(self):
        print("method 4 of class B")
    
class C(B):      #multi inheritance
    def method5(self):
        print("method 5 of class C")

class D():
    def method6(self):
        print("method 6 of class D")

class E(A,D):    #multiple inheritance
    def method7(self):
        print("method 7 of class E")

a1=A()    #this object can access all methods of class A
b1=B()    #this object can access all methods of A,B as A is parent of B
c1=C()    #this object can access all methods of A,B,C as B is parent of C
e1=E()    #this object can access all methods of A,D as A,D are parents of E
