import datetime


#--------create a account in bank system--------#
accounts=[]
def create_account():
    
    name=input("enter your name:")
    dob=input("enter your date of birth")
    dob_datetime = datetime.datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.date.today()
    age = today.year - dob_datetime.year - (
    (today.month, today.day) < (dob_datetime.month, dob_datetime.day)
     )
  
    if age<18:
        print("you are not eligible to create account")
        return
    address=input("enter your address:")
    phone=input("enter your phone number:")
    email=input("enter your mail id:")
    account_type=input("enter your account type(savings/current):")
    intial_deposit=float(input("enter intial deposit amount:"))
    if account_type.lower()=='savings' and intial_deposit<500:
        print("minimum balance for savings account is 500")
        return
    elif account_type.lower()=='current' and intial_deposit<1000:
        print("min balnce for account is 1000")
        return 
    account={
        'name':name,
        'dob':dob_datetime,
        'age':age,
        'address':address,
        'phone':phone,
        'email':email,
        'acccount_type':account_type,
    }
    accounts.append(account)
    print("account created successfully")
def check_balance(account):
    balance=1000000
    correct_pin=685457
    user=int(input("enter the pin"))
    i=0
    attempts=0
    while i <3:
        if user==correct_pin:
            print("enter succesfully on your account")
            print("current balance:",balance)
        else:
            print("invalid number")
        if attempts==3:
            print("soory sir")
        
def withdraw_balance():
    amount=int(input("enter the ammount withdraw"))
    if amount>balance:
        print("the balance invalid")
    else:
        print("the amount is withdraw")
        balance -= amount

def deposit_balance():
    amount_deposit=int(input("enter the amount"))
    balance += amount_deposit
    print("the amounnt is deposited:",balance)

def pin_change():
    correct_pin=685457
    new_pin=0
    user=int(input("enter the pin"))
    if user == correct_pin:
        print("enter the new pin")
        correct_pin==new_pin
        print("the pin is updated")
    else:
        print("get lost")
    
    new_pin.append(correct_pin)

def customer_service():
    print("use our service")
    print("1) user detail in bank")
    print("2) account information")
    print("3) pin change")
    print("4)call our service")
    print("5 exit")

    choice=0
    if choice==1:
        correct_pin=685457
        user=int(input("enter the pin")) 
        if user==correct_pin:
            print(create_account)
        else:
            print("invalid pin")
    elif choice==2:
            check_balance()
    elif choice==3:
            pin_change()
    elif choice==4:
            print("our service is under construction")
    elif choice==5:
            print("thank you for using our service")
    else:
          print("invalid choice")
          customer_service()

def main():
     print("welocme to bank systrem")

     while True:
          customer_service()
          print("what can we help you")
          print("1) create account")
          print("2)check balance")
          print("3) withdraw balance")
          print("4) deposit balance")
          print("5) pin. change")
          print("6) exit")

          choice=0
          if choice==1:
               create_account()
          elif choice==2:
               check_balance()
          elif choice==3:
               withdraw_balance()
          elif choice==4:
               deposit_balance()
          elif choice==5:
               pin_change()
          elif choice==6:
               print("thank you for using our service")
               break
          else:
               print("invalid choice")

        


    