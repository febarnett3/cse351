"""
Course    : CSE 351
Assignment: 02
Student   : Fiona Barnett

Instructions:
    - review instructions in the course
"""

# Don't import any other packages for this assignment
import os
import random
import threading
from money import *
from cse351 import Log

# ---------------------------------------------------------------------------
def main(): 
    print('\nATM Processing Program:')
    print('=======================\n')

    create_data_files_if_needed()

    # Load ATM data files
    data_files = get_filenames('data_files')
    
    log = Log(show_terminal=True)
    log.start_timer()

    bank = Bank()

    # create list to store threads
    threads = []

    # use the ATMReader and ATMReaderThread classes
    for file_name in data_files:
        reader = ATMReader(file_name, bank) # handles file and logic
        thread = ATMReaderThread(reader) # wraps reader in a thread
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # wait for all threads to finish

    test_balances(bank)
    log.stop_timer('Total time')

# ===========================================================================
class ATMReader:
    def __init__(self, file_name, bank):
        self.file_name = file_name
        self.bank = bank

    def process(self):
        with open(self.file_name, 'r') as file:
            for line in file:
                line = line.strip()

                if line.startswith('#') or not line:
                    continue

                parts = line.split(",")
                if len(parts) != 3:
                    continue

                try:
                    account_num = int(parts[0])
                    transaction_type = parts[1]
                    amount = parts[2].strip()

                    self.bank.addAccount(account_num)

                    if transaction_type == "d":
                        self.bank.deposit(account_num, amount)
                    elif transaction_type == "w":
                        self.bank.withdraw(account_num, amount)

                except ValueError as e:
                    print(f"Skipping invalid line: {line}, Error: {e}")
        

class ATMReaderThread(threading.Thread):
    def __init__(self, reader: ATMReader):
        super().__init__()  # Initialize the Thread
        self.reader = reader

    def run(self):
        self.reader.process()


class Account():
    def __init__(self, account_number):
        self.account_number = account_number
        self.balance = Money("0.00")  # Initial balance as Money object
    
    def deposit(self, amount):
        """Handle deposit by adding money"""
        self.balance.add(Money(str(amount)))  # Ensure amount is a valid string
    
    def withdraw(self, amount):
        """Handle withdrawal by subtracting money"""
        self.balance.sub(Money(str(amount)))  # Ensure amount is a valid string
    
    def get_balance(self):
        return self.balance  # Return balance as Money object


class Bank():
    def __init__(self):
        self.accounts = {}
        self.lock = threading.Lock()

    def addAccount(self, account_number):
        """Add account if it doesn't already exist"""
        with self.lock:
            if account_number not in self.accounts:
                new_account = Account(account_number)
                self.accounts[account_number] = new_account

    def deposit(self, account_num, amount):
        """Deposit the amount to the specified account"""
        with self.lock:
            if account_num in self.accounts:
                selected_account = self.accounts[account_num]
                selected_account.deposit(amount)

    def withdraw(self, account_num, amount):
        """Withdraw the amount from the specified account"""
        with self.lock:
            if account_num in self.accounts:
                selected_account = self.accounts[account_num]
                selected_account.withdraw(amount)

    def get_balance(self, account_num):
        with self.lock:
            if account_num in self.accounts:
                selected_account = self.accounts[account_num]
                return selected_account.get_balance()
            else:
                return Money("0.00")  # Optional fallback
        
    # TODO - implement this class here
#     accounts: dictionary
    # +__init__()
    # +deposit(account, amount) : void
    # +withdraw(account, amount) : void
    # +get_balance(account)


# ---------------------------------------------------------------------------

def get_filenames(folder):
    """ Don't Change """
    filenames = []
    for filename in os.listdir(folder):
        if filename.endswith(".dat"):
            filenames.append(os.path.join(folder, filename))
    return filenames

# ---------------------------------------------------------------------------
def create_data_files_if_needed():
    """ Don't Change """
    ATMS = 10
    ACCOUNTS = 20
    TRANSACTIONS = 250000

    sub_dir = 'data_files'
    if os.path.exists(sub_dir):
        return

    print('Creating Data Files: (Only runs once)')
    os.makedirs(sub_dir)

    random.seed(102030)
    mean = 100.00
    std_dev = 50.00

    for atm in range(1, ATMS + 1):
        filename = f'{sub_dir}/atm-{atm:02d}.dat'
        print(f'- {filename}')
        with open(filename, 'w') as f:
            f.write(f'# Atm transactions from machine {atm:02d}\n')
            f.write('# format: account number, type, amount\n')

            # create random transactions
            for i in range(TRANSACTIONS):
                account = random.randint(1, ACCOUNTS)
                trans_type = 'd' if random.randint(0, 1) == 0 else 'w'
                amount = f'{(random.gauss(mean, std_dev)):0.2f}'
                f.write(f'{account},{trans_type},{amount}\n')

    print()

# ---------------------------------------------------------------------------
def test_balances(bank):
    """ Don't Change """

    # Verify balances for each account
    correct_results = (
        (1, '59362.93'),
        (2, '11988.60'),
        (3, '35982.34'),
        (4, '-22474.29'),
        (5, '11998.99'),
        (6, '-42110.72'),
        (7, '-3038.78'),
        (8, '18118.83'),
        (9, '35529.50'),
        (10, '2722.01'),
        (11, '11194.88'),
        (12, '-37512.97'),
        (13, '-21252.47'),
        (14, '41287.06'),
        (15, '7766.52'),
        (16, '-26820.11'),
        (17, '15792.78'),
        (18, '-12626.83'),
        (19, '-59303.54'),
        (20, '-47460.38'),
    )

    wrong = False
    for account_number, balance in correct_results:
        bal = bank.get_balance(account_number)
        print(f'{account_number:02d}: balance = {bal}')
        if Money(balance) != bal:
            wrong = True
            print(f'Wrong Balance: account = {account_number}, expected = {balance}, actual = {bal}')

    if not wrong:
        print('\nAll account balances are correct')



if __name__ == "__main__":
    main()

