

class Account:

    amount = 0.0
    def __init__(self):
        pass
    
    @classmethod
    def deposit(self, amount):
        self.amount += amount
        print(f"New Balance: ${self.amount}")
    
    def withdraw(self, amount):
        if self.amount - amount <= 0:
            print('error - insufficient funds')
        else:
            new_balance = self.amount - amount
            print(f"Withdraw: ${amount} approved. Remaining Balance: ${new_balance}")
            self.amount = new_balance


# acct = Account()
# for i in range(0,50,2):
#     acct.deposit(i * 2)

def test_decorator(func):
    def wrapper():
        print('before function call')
        func()
        print('after function call')
    return wrapper

@test_decorator
def say_hello():
    print('hello, world!')

say_hello()
