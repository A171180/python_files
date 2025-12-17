from string import ascii_uppercase
import random

def generate_love_percentage(name1, name2):
    combined_names = (name1 + name2).lower()

    true_count = (
        combined_names.count('t') +
        combined_names.count('r') +
        combined_names.count('u') +
        combined_names.count('e')
    )

    love_count = (
        combined_names.count('l') +
        combined_names.count('o') +
        combined_names.count('v') +
        combined_names.count('e')
    )

    love_percentage = int(str(true_count) + str(love_count))
    return love_percentage


def generate_password(name1, name2):
    combined_names = name1 + name2
    password_length = max(8, len(combined_names))
    password = ''.join(random.choice(ascii_uppercase) for _ in range(password_length))
    return password


def message_with_love_percentage(name1, name2):
    love_percentage = generate_love_percentage(name1, name2)

    print(f"\nLove Percentage: {love_percentage}%")

    if love_percentage < 80:
        print("Every time I think of you, my heart smiles without any reason.")
    elif 80 <= love_percentage <= 95:
        print("Your love is strong and beautiful ❤️")
    else:
        print("This love is extremely powerful 🔥")


def main():
    print("------------ LOVE PROGRAM ------------")
    print("1. Calculate Love Percentage")
    print("2. Generate Password")
    print("3. Love Message")

    choice = int(input("Enter your choice: "))

    name1 = input("Enter your name: ")
    name2 = input("Enter your partner name: ")

    if choice == 1:
        result = generate_love_percentage(name1, name2)
        print(f"Love Percentage: {result}%")

    elif choice == 2:
        password = generate_password(name1, name2)
        print("Generated Password:", password)

    elif choice == 3:
        message_with_love_percentage(name1, name2)

    else:
        print("Invalid choice")


main()