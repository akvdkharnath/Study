# Object-Oriented Programming (OOP) in Python: Complete Guide for Senior Developers

## Table of Contents
1. [Beginner Fundamentals](#beginner-fundamentals)
2. [Intermediate Concepts](#intermediate-concepts)
3. [Advanced Topics](#advanced-topics)
4. [Professional-Level Mastery](#professional-level-mastery)
5. [Interview Preparation](#interview-preparation)

---

## BEGINNER FUNDAMENTALS

### 1. Classes and Objects - The Foundation

**What is a Class?**
A class is a blueprint for creating objects. It defines the structure (attributes) and behavior (methods) that instances of that class will have.

**What is an Object?**
An object is an instance of a class. It's a concrete realization of the blueprint with actual data.

#### Basic Class Definition

```python
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis familiaris"
    
    # Constructor - initializes instance attributes
    def __init__(self, name, age):
        self.name = name  # Instance attribute
        self.age = age
    
    # Instance method
    def speak(self, sound):
        return f"{self.name} says {sound}"
    
    # String representation
    def __str__(self):
        return f"{self.name} is {self.age} years old"

# Creating objects (instantiation)
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(dog1.species)  # Output: Canis familiaris (class attribute)
print(dog1.name)     # Output: Buddy (instance attribute)
print(dog1.speak("Woof"))  # Output: Buddy says Woof
```

**Key Concepts:**
- **`__init__()` (Constructor)**: Initializes instance attributes when an object is created
- **`self`**: Represents the instance itself; must be the first parameter in instance methods
- **Class Attributes**: Shared by all instances
- **Instance Attributes**: Unique to each instance

### 2. Instance vs Class Attributes

```python
class BankAccount:
    # Class attribute - shared across all instances
    interest_rate = 0.03
    
    def __init__(self, account_holder, balance):
        # Instance attributes - unique to each instance
        self.account_holder = account_holder
        self.balance = balance
    
    def get_interest(self):
        return self.balance * BankAccount.interest_rate

# Test
account1 = BankAccount("Alice", 1000)
account2 = BankAccount("Bob", 2000)

print(account1.interest_rate)  # 0.03
print(account2.balance)         # 2000
print(account1.balance)         # 1000

# Modifying class attribute
BankAccount.interest_rate = 0.04
print(account1.get_interest())  # 40 (using new rate)
```

### 3. Types of Methods

```python
class Employee:
    company_name = "TechCorp"
    
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    # Instance method
    def give_raise(self, amount):
        self.salary += amount
        return f"{self.name} now earns ${self.salary}"
    
    # Class method (uses @classmethod decorator)
    @classmethod
    def from_string(cls, employee_str):
        """Create an instance from a string"""
        name, salary = employee_str.split(',')
        return cls(name, int(salary))
    
    # Static method (uses @staticmethod decorator)
    @staticmethod
    def is_valid_salary(salary):
        """Check if salary is valid (doesn't use instance or class)"""
        return salary > 0

# Instance method
emp = Employee("John", 50000)
print(emp.give_raise(5000))  # Output: John now earns $55000

# Class method
emp2 = Employee.from_string("Jane,60000")
print(emp2.name, emp2.salary)  # Output: Jane 60000

# Static method
print(Employee.is_valid_salary(50000))  # Output: True
print(Employee.is_valid_salary(-1000))  # Output: False
```

**Key Differences:**
- **Instance Method**: Can access and modify instance/class data via `self`
- **Class Method**: Can access/modify class data via `cls`; called with `@classmethod`
- **Static Method**: Cannot access instance or class data; utility functions; called with `@staticmethod`

### 4. Special Methods (Dunder Methods)

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    # String representation (for print())
    def __str__(self):
        return f"Person: {self.name}, Age: {self.age}"
    
    # Developer representation (for debugging)
    def __repr__(self):
        return f"Person('{self.name}', {self.age})"
    
    # Equality comparison
    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.age == other.age
    
    # Less than comparison
    def __lt__(self, other):
        return self.age < other.age
    
    # String length (custom behavior)
    def __len__(self):
        return len(self.name)
    
    # Make object callable
    def __call__(self, greeting):
        return f"{self.name} says: {greeting}"

# Test
p1 = Person("Alice", 30)
p2 = Person("Bob", 25)

print(p1)           # Output: Person: Alice, Age: 30
print(repr(p1))     # Output: Person('Alice', 30)
print(p1 == p2)     # Output: False
print(p2 < p1)      # Output: True (Bob is younger)
print(len(p1))      # Output: 5 (length of "Alice")
print(p1("Hello"))  # Output: Alice says: Hello
```

---

## INTERMEDIATE CONCEPTS

### 1. Inheritance - Code Reuse

Inheritance allows a child class to inherit attributes and methods from a parent class.

#### Single Inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):  # Dog inherits from Animal
    def speak(self):  # Overriding parent method
        return f"{self.name} barks: Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} meows: Meow!"

# Test
dog = Dog("Rex")
cat = Cat("Whiskers")

print(dog.speak())  # Output: Rex barks: Woof!
print(cat.speak())  # Output: Whiskers meows: Meow!
```

#### Using super() - Extending Parent Behavior

```python
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    
    def description(self):
        return f"{self.brand} {self.model}"

class Car(Vehicle):
    def __init__(self, brand, model, num_doors):
        super().__init__(brand, model)  # Call parent constructor
        self.num_doors = num_doors
    
    def description(self):
        # Extend parent behavior
        parent_desc = super().description()
        return f"{parent_desc} with {self.num_doors} doors"

# Test
car = Car("Toyota", "Camry", 4)
print(car.description())  # Output: Toyota Camry with 4 doors
```

#### Multiple Inheritance

```python
class Flyer:
    def fly(self):
        return "Flying high!"

class Swimmer:
    def swim(self):
        return "Swimming deep!"

class Duck(Flyer, Swimmer):
    def quack(self):
        return "Quack!"

# Test
duck = Duck()
print(duck.fly())    # Output: Flying high!
print(duck.swim())   # Output: Swimming deep!
print(duck.quack())  # Output: Quack!

# Check MRO (Method Resolution Order)
print(Duck.__mro__)  # Shows the order Python looks for methods
```

**Method Resolution Order (MRO)**:
Python uses C3 Linearization to determine which class method to call in inheritance hierarchies.

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

d = D()
print(d.method())  # Output: B (following MRO: D -> B -> C -> A)
print(D.__mro__)   # Shows MRO order
```

### 2. Encapsulation - Data Protection

Encapsulation hides internal details and protects data through access control.

```python
class BankAccount:
    def __init__(self, account_number, balance):
        self.__account_number = account_number  # Private (name mangling)
        self._balance = balance  # Protected (convention)
        self.currency = "USD"  # Public
    
    # Getter
    def get_balance(self):
        return self._balance
    
    # Setter with validation
    def set_balance(self, amount):
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = amount
    
    # Encapsulated behavior
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
    
    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount

# Test
account = BankAccount("123456", 1000)
print(account.get_balance())  # 1000
account.deposit(500)
print(account.get_balance())  # 1500
account.withdraw(200)
print(account.get_balance())  # 1300

# Cannot directly access private attribute (though it's still accessible via name mangling)
# print(account.__account_number)  # Would raise AttributeError
print(account._BankAccount__account_number)  # Name mangling - not recommended
```

**Access Levels:**
- **Public** (no underscore): Accessible from anywhere
- **Protected** (`_name`): Convention indicating internal use
- **Private** (`__name`): Name mangling; Python manges it to `_ClassName__name`

### 3. Polymorphism - Many Forms

Polymorphism allows objects of different types to be treated through the same interface.

```python
class Shape:
    def area(self):
        raise NotImplementedError("Subclasses must implement area()")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def area(self):
        return 0.5 * self.base * self.height

# Polymorphic function
def print_area(shape):
    print(f"Area: {shape.area()}")

# Test - same function works with different types
shapes = [Circle(5), Rectangle(4, 6), Triangle(4, 3)]
for shape in shapes:
    print_area(shape)

# Output:
# Area: 78.5
# Area: 24
# Area: 6.0
```

**Duck Typing - Python's Way**:
Python doesn't require objects to inherit from a base class. It uses "if it quacks like a duck, it's a duck."

```python
class Dog:
    def speak(self):
        return "Woof!"

class Person:
    def speak(self):
        return "Hello!"

class Robot:
    def speak(self):
        return "Beep boop!"

# All can be used interchangeably
def make_it_speak(thing):
    print(thing.speak())

make_it_speak(Dog())    # Output: Woof!
make_it_speak(Person()) # Output: Hello!
make_it_speak(Robot())  # Output: Beep boop!
```

---

## ADVANCED TOPICS

### 1. Descriptors - Advanced Attribute Management

Descriptors implement the descriptor protocol to customize attribute access.

```python
class Descriptor:
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
    
    def __delete__(self, obj):
        del obj.__dict__[self.name]

# Practical example: Validated number descriptor
class ValidatedNumber:
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, 0)
    
    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected int or float, got {type(value)}")
        if value < 0:
            raise ValueError("Value must be non-negative")
        obj.__dict__[self.name] = value

class Product:
    price = ValidatedNumber()
    quantity = ValidatedNumber()
    
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

# Test
product = Product("Laptop", 999.99, 5)
print(product.price)    # 999.99

product.price = 1299.99  # OK
# product.price = -100   # Raises ValueError
# product.price = "free" # Raises TypeError
```

**Key Methods:**
- `__get__()`: Called when attribute is accessed
- `__set__()`: Called when attribute is assigned
- `__delete__()`: Called when attribute is deleted
- `__set_name__()`: Called when descriptor is assigned to class attribute (Python 3.6+)

### 2. Properties - Pythonic Attribute Access

Properties use the `@property` decorator to create getters, setters, and deleters.

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    # Getter - accessed like an attribute
    @property
    def celsius(self):
        return self._celsius
    
    # Setter - called when assigned
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value
    
    # Deleter - called with del
    @celsius.deleter
    def celsius(self):
        del self._celsius
    
    # Computed property
    @property
    def fahrenheit(self):
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self._celsius = (value - 32) * 5/9

# Test
temp = Temperature(25)
print(temp.celsius)      # 25 (getter)
print(temp.fahrenheit)   # 77.0 (computed)

temp.fahrenheit = 86     # setter
print(temp.celsius)      # 30 (converted)

del temp.celsius         # deleter
# print(temp.celsius)    # Would raise AttributeError
```

**When to Use Properties:**
- Validating data on assignment
- Computing values on access
- Changing implementation without breaking API
- Creating read-only or write-only attributes

### 3. Abstract Base Classes - Enforcing Contracts

Abstract Base Classes (ABCs) enforce that subclasses implement required methods.

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        """Subclasses must implement speak()"""
        pass
    
    @abstractmethod
    def move(self):
        pass
    
    # Concrete method in abstract class
    def describe(self):
        return f"This is a {self.__class__.__name__}"

class Dog(Animal):
    def speak(self):
        return "Woof!"
    
    def move(self):
        return "Running on four legs"

class Bird(Animal):
    def speak(self):
        return "Tweet!"
    
    def move(self):
        return "Flying"

# Test
dog = Dog()
print(dog.speak())      # Output: Woof!
print(dog.describe())   # Output: This is a Dog

# This would raise TypeError:
# animal = Animal()  # Cannot instantiate abstract class

# Verify inheritance
print(isinstance(dog, Animal))  # True
```

### 4. Metaclasses - Classes That Create Classes

Metaclasses are classes whose instances are classes.

```python
# Simple metaclass example
class SingletonMeta(type):
    """Metaclass that ensures only one instance exists"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected to DB"
    
    def query(self, sql):
        return f"Executing: {sql}"

# Test
db1 = Database()
db2 = Database()

print(db1 is db2)  # True (same instance)
print(db1.query("SELECT * FROM users"))
```

**When to Use Metaclasses:**
- Implementing design patterns (Singleton, Factory)
- Framework development
- Automatic registration of subclasses
- Custom class creation behavior

### 5. Context Managers - Resource Management

Context managers handle setup and cleanup using `with` statements.

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """Called when entering 'with' block"""
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block"""
        if self.file:
            self.file.close()
        # Return True to suppress exceptions
        return False

# Test
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")
# File is automatically closed

# Using contextlib decorator (simpler)
from contextlib import contextmanager

@contextmanager
def database_connection(host):
    print(f"Connecting to {host}...")
    # Yield the resource
    yield f"Connection to {host}"
    print(f"Closing connection to {host}...")

with database_connection("localhost") as conn:
    print(f"Using {conn}")
```

---

## PROFESSIONAL-LEVEL MASTERY

### 1. SOLID Principles

#### Single Responsibility Principle (SRP)

```python
# Bad - multiple responsibilities
class User:
    def save_to_db(self, user_data):
        # Database logic
        pass
    
    def send_email(self, email, message):
        # Email logic
        pass
    
    def generate_report(self):
        # Report logic
        pass

# Good - separated responsibilities
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user):
        # Only handles persistence
        pass

class EmailService:
    def send(self, email, message):
        # Only handles email
        pass

class ReportGenerator:
    def generate(self, user):
        # Only handles reports
        pass
```

#### Open-Closed Principle (OCP)

```python
# Bad - needs modification to extend
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == "credit":
            return amount * 1.02  # 2% fee
        elif payment_type == "debit":
            return amount * 1.01  # 1% fee
        elif payment_type == "crypto":
            return amount * 1.05  # 5% fee

# Good - open for extension, closed for modification
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardPayment(PaymentMethod):
    def process(self, amount):
        return amount * 1.02

class DebitCardPayment(PaymentMethod):
    def process(self, amount):
        return amount * 1.01

class CryptoPayment(PaymentMethod):
    def process(self, amount):
        return amount * 1.05

class PaymentProcessor:
    def process(self, payment_method, amount):
        return payment_method.process(amount)
```

#### Liskov Substitution Principle (LSP)

```python
# Bad - Square violates LSP
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Violates expectations
    
    def set_height(self, height):
        self.width = height
        self.height = height

# Good - use composition or separate hierarchy
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side
    
    def area(self):
        return self.side ** 2
```

#### Interface Segregation Principle (ISP)

```python
# Bad - Clients forced to implement unnecessary methods
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass
    
    @abstractmethod
    def eat_lunch(self):
        pass

class Robot(Worker):
    def work(self):
        return "Working..."
    
    def eat_lunch(self):
        raise NotImplementedError("Robots don't eat")

# Good - Segregate interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat_lunch(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        return "Working..."
    
    def eat_lunch(self):
        return "Eating..."

class Robot(Workable):
    def work(self):
        return "Working..."
```

#### Dependency Inversion Principle (DIP)

```python
# Bad - depends on concrete classes
class MySQLDatabase:
    def save(self, data):
        print(f"Saving to MySQL: {data}")

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Tight coupling
    
    def save_user(self, user):
        self.db.save(user)

# Good - depends on abstractions
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        print(f"Saving to MySQL: {data}")

class MongoDatabase(Database):
    def save(self, data):
        print(f"Saving to MongoDB: {data}")

class UserService:
    def __init__(self, database: Database):
        self.db = database  # Depends on abstraction
    
    def save_user(self, user):
        self.db.save(user)

# Can switch databases easily
mysql_db = MySQLDatabase()
mongo_db = MongoDatabase()

service1 = UserService(mysql_db)
service2 = UserService(mongo_db)
```

### 2. Design Patterns

#### Singleton Pattern

```python
class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Configuration(metaclass=Singleton):
    def __init__(self):
        self.settings = {}
    
    def get(self, key):
        return self.settings.get(key)
    
    def set(self, key, value):
        self.settings[key] = value

# Test
config1 = Configuration()
config2 = Configuration()
assert config1 is config2  # Same instance
```

#### Factory Pattern

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal: {animal_type}")

# Test
animal = AnimalFactory.create_animal("dog")
print(animal.speak())  # Output: Woof!
```

#### Observer Pattern

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass

class EmailObserver(Observer):
    def update(self, event):
        print(f"Email sent: {event}")

class LogObserver(Observer):
    def update(self, event):
        print(f"Event logged: {event}")

# Test
subject = Subject()
email_obs = EmailObserver()
log_obs = LogObserver()

subject.attach(email_obs)
subject.attach(log_obs)
subject.notify("User registered")
```

---

## INTERVIEW PREPARATION

### Common Interview Questions & Answers

**Q1: What's the difference between `__init__` and `__new__`?**

```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        """Called first to create the instance"""
        print("__new__ called")
        return super().__new__(cls)
    
    def __init__(self, value):
        """Called after __new__ to initialize the instance"""
        print("__init__ called")
        self.value = value

obj = MyClass(42)
# Output:
# __new__ called
# __init__ called
```

**Q2: Explain Method Resolution Order (MRO)**

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

# C3 Linearization
print(D.__mro__)  # Shows: D -> B -> C -> A -> object
# Follows: depth-first, left-to-right, but parents before children
```

**Q3: What are Python's access modifiers?**

```python
class Example:
    public = "Public"           # Accessible everywhere
    _protected = "Protected"    # Convention: for internal use
    __private = "Private"       # Name mangled to _Example__private

obj = Example()
print(obj.public)              # OK
print(obj._protected)          # OK (but discouraged)
print(obj._Example__private)   # OK (but very discouraged)
# print(obj.__private)         # AttributeError
```

**Q4: Explain the `super()` function**

```python
class Parent:
    def method(self):
        return "Parent"

class Child(Parent):
    def method(self):
        parent_result = super().method()
        return f"{parent_result} + Child"

child = Child()
print(child.method())  # Output: Parent + Child
```

**Q5: What's the difference between a class method and static method?**

| Aspect | Instance Method | Class Method | Static Method |
|--------|-----------------|--------------|---------------|
| Decorator | None | `@classmethod` | `@staticmethod` |
| First param | `self` | `cls` | None |
| Access instance data | Yes | No | No |
| Access class data | Yes | Yes | No |
| Can modify state | Yes (instance) | Yes (class) | No |

**Q6: What are descriptors and when would you use them?**

```python
# Descriptor protocol
class Descriptor:
    def __get__(self, obj, type=None):
        # Called on attribute access
        pass
    
    def __set__(self, obj, value):
        # Called on attribute assignment
        pass
    
    def __delete__(self, obj):
        # Called on attribute deletion
        pass

# Use case: Property validation
class ValidatedString:
    def __init__(self, max_length):
        self.max_length = max_length
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if len(value) > self.max_length:
            raise ValueError(f"String too long (max {self.max_length})")
        obj.__dict__[self.name] = value

class User:
    name = ValidatedString(50)
    email = ValidatedString(100)

user = User()
user.name = "John Doe"  # OK
# user.name = "X" * 100  # Raises ValueError
```

**Q7: Implement a simple Singleton pattern**

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Or using metaclass
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseConnection(metaclass=SingletonMeta):
    pass

db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # True
```

**Q8: What's the difference between composition and inheritance?**

```python
# Inheritance (IS-A relationship)
class Animal:
    def breathe(self):
        return "Breathing"

class Dog(Animal):
    pass

# Composition (HAS-A relationship)
class Engine:
    def start(self):
        return "Engine started"

class Car:
    def __init__(self):
        self.engine = Engine()  # Has-a relationship
    
    def start(self):
        return self.engine.start()

# Best practice: Composition is more flexible
class Vehicle:
    def __init__(self, engine):
        self.engine = engine

class GasEngine:
    def start(self):
        return "Gas engine started"

class ElectricEngine:
    def start(self):
        return "Electric engine started"

car = Vehicle(GasEngine())  # Easy to swap engines
```

### Performance Optimization Tips

```python
# 1. Use __slots__ to reduce memory usage
class Point:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 2. Lazy loading for expensive operations
class DataObject:
    def __init__(self):
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = self._load_data()
        return self._data
    
    def _load_data(self):
        # Expensive operation
        return "Loaded data"

# 3. Use weak references to prevent circular references
import weakref

class Observer:
    def __init__(self, callback):
        self.callback = weakref.ref(callback)
```

### Final Checklist for Senior Developer Interviews

✓ Understand classes, objects, and attributes
✓ Master inheritance (single, multiple, MRO)
✓ Implement encapsulation with access modifiers
✓ Know when to use polymorphism and duck typing
✓ Understand descriptors and properties
✓ Implement metaclasses correctly
✓ Apply SOLID principles
✓ Know common design patterns (Singleton, Factory, Observer)
✓ Understand context managers and `with` statement
✓ Optimize code using `__slots__` and lazy loading
✓ Handle exceptions appropriately
✓ Write testable OOP code

---

## Conclusion

Object-Oriented Programming in Python is a powerful paradigm that enables you to write clean, maintainable, and scalable code. From basic classes to advanced metaclasses, Python provides flexible tools for every scenario. Master these concepts to excel in senior developer roles and technical interviews.
