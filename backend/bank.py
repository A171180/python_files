import datetime

accounts = []

def create_account():
    name = input("Enter your name: ")
    dob = input("Enter DOB (dd-mm-yyyy): ")

    dob_datetime = datetime.datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.date.today()

    age = today.year - dob_datetime.year - (
        (today.month, today.day) < (dob_datetime.month, dob_datetime.day)
    )

    if age < 18:
        print("Not eligible")
        return

    balance = float(input("Enter initial deposit: "))

    account = {
        "name": name,
        "age": age,
        "balance": balance,
        "pin": 1234
    }

    accounts.append(account)
    print("Account created")

def main():
    create_account()

main()
