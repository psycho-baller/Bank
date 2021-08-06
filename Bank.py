from random import randint
import sqlite3
conn = sqlite3.connect('card.sqlite')
cur = conn.cursor()

class BankAccount:
    accounts = []

    def __init__(self, card_number, pin, balance):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance
        BankAccount.accounts.append(self)


def generate_account():
    bin = '400000'
    card = ''.join(str(randint(0, 9)) for _ in range(9))
    streets = list(bin + card)
    card_list = [int(x) for x in streets]
    for x in range(0, 15, 2):
        card_list[x] = card_list[x]*2
    for x in range(0, 15, 1):
        if card_list[x] > 9:
            card_list[x] = card_list[x] - 9
    target = sum(card_list)
    last_digit = 0
    while True:
        if (target + last_digit) % 10 == 0:
            break
        else:
            last_digit += 1
    return bin + card + str(last_digit)

def generate_pin():
    while True:
        pinn =  ''.join(str(randint(0, 9)) for _ in range(4))
        if len(pinn) == 4:
            return pinn


def create_account():
    new_acc = BankAccount(generate_account(), generate_pin(), 0)
    cur.execute(f'INSERT INTO card (number, pin) VALUES ( {new_acc.card_number} , {new_acc.pin});')
    
    print('\nYour card has been created',
          'Your card number:',
          new_acc.card_number,
          'Your card PIN:',
          new_acc.pin,
          sep='\n')
    print()

def login():
    if not BankAccount.accounts:
        return None

    login_card = str(input('\nEnter your card number:\n'))
    login_pin =  str(input('Enter your PIN:\n'))

    for account in BankAccount.accounts:
        if login_card == account.card_number and login_pin == account.pin:
            return account
    return None

    
def check_luhn(card_no):
    n_digits = len(card_no)
    n_sum = 0
    is_second = False
    for i in range(n_digits - 1, -1, -1):
        d = ord(card_no[i]) - ord('0')
        if (is_second == True):
            d = d * 2
        n_sum += d // 10
        n_sum += d % 10
        is_second = not is_second
     
    if (n_sum % 10 == 0):
        return True
    else:
        return False
    
def exists(card_no):
    for x in BankAccount.accounts:
        if card_no == x.card_number:
            return True
    return None

def account_actions(account):
    user_menu = ('1. Balance','2. Add income', '3. Do transfer','4. Close account', '5. Log out', '0. Exit')
    while True:
        conn.commit()
        print(*user_menu, sep='\n')
        user_input = int(input('>'))

        if user_input == 1:
            print('\nBalance:', str(cur.execute(f'SELECT balance FROM card WHERE number = {account.card_number}').fetchone()).strip('(,)'),'\n')
        
        elif user_input == 2:
            print('\nEnter income:')
            add_ammount = int(input('>'))
            cur.execute(f'UPDATE card SET balance = balance + {add_ammount} WHERE number = {account.card_number}')
            account.balance += add_ammount 
            print('income was added!\n')
        
        elif user_input == 3:
            print('\nTRANSFER')
            print('Enter card number:')
            card_num = input('>')
            if card_num == account.card_number:
                print("You can't transfer money to the same account!\n")
                continue              
            if not check_luhn(card_num):
                print('Probably you made a mistake in the card number. Please try again!\n')
                continue
            if not exists(card_num):
                print('Such a card does not exist\n')
                continue
            print('Enter how much money you want to transfer:')
            transfer_ammount = int(input('>'))
            if transfer_ammount > account.balance:
                print('Not enough money!')
                continue

            cur.execute(f'UPDATE card SET balance = balance - {transfer_ammount} WHERE number = {account.card_number}')
            cur.execute(f'UPDATE card SET balance = balance + {transfer_ammount} WHERE number = {card_num}')
            print('Success!')
            break
            
        elif user_input == 4:
            cur.execute(f'DELETE FROM card WHERE number = {account.card_number}')
            BankAccount.accounts.remove(account)
            print('\nThe account has been closed\n')
            break
        
        elif user_input == 5:
            print('\nYou have successfully logged out!\n')
            break
        elif user_input == 0:
            print('\nBye!')
            conn.close()
            exit()
        else:
            print('Only enter an number between 0 and 5\n')
            continue


cur.execute('''
CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY key,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0);''')

cur.execute('SELECT * FROM card')
rows = cur.fetchall()
for row in rows:
    BankAccount(row[1], row[2], row[3])


main_menu = ('1. Create an account', '2. Log into account', '0. Exit')
while True:
    conn.commit()
    print(*main_menu, sep='\n')
    user_input = int(input('>'))
    if user_input == 1:
        create_account()
    elif user_input == 2:
        logged_user = login()
        if logged_user:
            print('\nYou have successfully logged in!\n')
            account_actions(logged_user)
        elif not BankAccount.accounts:
            print('\nMake an account first\n')
        else:
            print('\nWrong card number or PIN!\n')
    elif user_input == 0:
        print('\nBye!')
        break
    else:
        print('Only enter 0, 1, or 2\n')
        continue
conn.close()    