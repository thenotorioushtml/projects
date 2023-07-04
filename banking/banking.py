import random  # Library used to randomly generate card numbers and pins
import sqlite3  # Library used for the database


class CreditCard:  # The object oof the credit card
    def __init__(self, bank_id, acc_id, pin_num):
        self.bin = bank_id
        self.acc_id = acc_id
        self.pin = pin_num

    def gen_crd_num(self):  # Generates and Luhn checks the random card number
        while True:
            self.bin = "400000"
            self.acc_id = str(random.randint(100000000, 999999999))
            string = self.bin + self.acc_id
            check_num = [int(x) for x in string]
            for i in range(0, len(check_num) + 1, 2):
                check_num[i] *= 2
                if check_num[i] > 9:
                    check_num[i] -= 9
            for a in range(10):
                if (sum(check_num) + a) % 10 == 0:
                    check_num.append(a)
                    return string + str(a)

    def generate_pin(self):   # Generates a simple pin
        self.pin = str(random.randint(1000, 9999))
        return str(self.pin)


def create_connection(db_file):  # Function that creates the connection to the accounts database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as error:
        print("Failed to create connection", error)
    return conn


def in_database(card, pin_to_database):  # Function that puts a newly created account into the database
    cur.execute(
        f'''INSERT INTO card(number, pin) 
        VALUES ({card}, {pin_to_database})
        ''')
    connection.commit()


def check_credentials(c_num, p_num):  # Function to check the credentials at the login
    cur.execute(f'''
    SELECT number, pin
    FROM card
    WHERE number = {c_num}
    AND pin = {p_num}
    ''')
    user_exists = cur.fetchone()
    if user_exists:
        return True
    else:
        return False


def check_balance(c_num):  # Function that returns the current balance of your account
    cur.execute(
        f'''
    SELECT pin, balance
    FROM card
    WHERE number = {c_num}
    ''')
    result = cur.fetchall()
    return result


def add_income(amount, c_num):  # Function to add money to the account
    cur.execute(f'''
    UPDATE card 
    SET balance = balance + {amount} 
    WHERE number = {c_num}
    ''')
    connection.commit()


def luhn_check(card_number):  # Function to check if the the given card number satisfies  the Luhn algorithm
    def digits_of(n):
        return [int(c) for c in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return (checksum % 10) == 0


def exists(card):  # Function to check if the card you want to make a transfer to exists
    cur.execute(f'''
    SELECT rowid
    FROM card
    WHERE number = {card}''')
    exists_card = cur.fetchone()
    if exists_card is None:
        return False
    else:
        return True


def can_transfer_money(card, amount):  # Function to check if your account can make the transfer
    balance_card = check_balance(card)
    if (balance_card[0][1] - amount) < 0:
        return False
    else:
        return True


def transfer(from_card, to_card, amount):  # Function that manages the transfers between the accounts
    sender = from_card
    receiver = to_card
    money = amount

    def subtract_from_sender(from_card_sub, amount_add):
        cur.execute(f'''
        UPDATE card
        SET balance = balance - {amount_add}
        WHERE number = {from_card_sub}''')
        connection.commit()

    def add_to_receiver(to_card_add, amount_sub):
        cur.execute(f'''
        UPDATE card
        SET balance = balance + {amount_sub}
        WHERE number = {to_card_add}''')
        connection.commit()
    subtract_from_sender(sender, money)
    add_to_receiver(receiver, money)


def delete_account(card_number):  # Function to delete the account
    cur.execute(f'''
    DELETE FROM card
    WHERE number = {card_number}''')
    connection.commit()


while True:  # The program itself starts here
    connection = create_connection("card.s3db")  # Creating a connection to the database of the accounts
    cur = connection.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS card(
        id INTEGER PRIMARY KEY, 
        number TEXT, 
        pin TEXT,
        balance INTEGER DEFAULT 0)
        ''')  # Creating the table of the values
    connection.commit()
    pin = None
    card_num = None
    choice = input("1. Create account\n2. Log into account\n0. Exit\n")
    if choice == "1":  # Creating the account and generating credentials
        generated_pin = CreditCard(0, 0, 00000).generate_pin()
        generated_card_num = CreditCard(0, 0, 0000).gen_crd_num()
        pin = int(generated_pin)
        card_num = int(generated_card_num)
        in_database(card_num, pin)
        print("Your card has been created\nYour card number:\n" + str(card_num) + "\nYour card PIN:\n" + str(pin))
    elif choice == "2":  # Login into account
        while True:  # Asking for credentials and checking them
            in_crd_num = input("Enter your card number:\n")
            in_pin = input("Enter your PIN:\n")
            if not check_credentials(in_crd_num, in_pin):  # If the credentials don't correspond
                print("Wrong card number or pin!")
                break
            elif check_credentials(in_crd_num, in_pin):  # If the credentials are OK
                print("You have successfully logged in!\n")
                while True:   # Entering the account after a successful authentication
                    choice = input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
                    if choice == "1":  # Checking the account balance
                        balance = check_balance(in_crd_num)
                        print("Balance " + str(balance[0][1]) + "\n")
                    elif choice == "2":  # Adding money to the account
                        how_much = int(input("How much do you want to deposit?:\n"))
                        add_income(how_much, in_crd_num)
                        print("Amount deposited!\n")
                    elif choice == "3":  # Making a transfer of the money to another account
                        while True:
                            trans_card_number = int(input("Where do you want to transfer the money?:\n"))
                            if not luhn_check(trans_card_number):  # Checks if the card number is Luhn proof
                                print("Probably you made a mistake in the card number. Please try again!\n")
                                break
                            elif not exists(trans_card_number):  # Checks  if the card number exist in the database
                                print("Such a card does not exists.\n")
                                break
                            elif in_crd_num == trans_card_number:  # Checks whether the card number of the sender is the
                                # as the card number of the receiver
                                print("You can't transfer money to the same account!\n")
                                break
                            trans_amount_money = int(input("How much do you want to transfer?:\n"))
                            if not can_transfer_money(in_crd_num, trans_amount_money):  # Checks if the amount you want
                                # to send is not bigger than your balance
                                print("Not enough money!\n")
                                break
                            else:
                                transfer(in_crd_num, trans_card_number, trans_amount_money)  # Transfers the money after
                                # all checks
                                print("Success!\n")
                                break
                            break
                    elif choice == "4":  # Deleting the account from the system
                        delete_account(in_crd_num)
                        print("The account has been closed!\n")
                        break  # Breaks from the deposit loop
                    elif choice == "5":
                        print("You have successfully logged out!\n")
                        break
                    elif choice == "0":
                        print("Bye!\n")
                        quit()
            break  # Breaks from the account loop
    elif choice == "0":
        print("Bye!\n")
        quit()
