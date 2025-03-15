'''
    Demonstrates how to do Object-Oriented Programming in Python
    
    1. Encapsulation (handling public vs private methods)
    2. Inheritance (allows one class to inherit attributes and methods from another class).
    3. Polymorphism (allows different classes to define the same method in different ways!)
    4. Abstraction
'''

# 1. Encapsulation
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner          # Public attribute
        self.__balance = balance    # Private attribute (use '__')
    
    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount > self.__balance:
            print('Insufficient Funds')

        else:
            self.__balance -= amount 

    def get_balance(self):
        return self.__balance
    
# invoking code:
account = BankAccount("Alice", 1000)
account.deposit(500)
#print(account.get_balance()) # works and outputs 1500 (1000 + 500)
#print(account.__balance) #errors because __balance is a PRIVATE attribute. (results in AttributeError)

# 2. Inheritance

#Parent Class
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

# child classes:
class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())
print(cat.speak())

# 3. Polymorphism
class Shape:
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius * self.radius
    
class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height
    
shapes = [Circle(5), Rectangle(4,6)]

for shape in shapes:
    print(shape.area())

