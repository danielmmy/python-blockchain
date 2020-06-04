from block import Block
from blockchain import Blockchain
from transaction import Transaction
from uuid import uuid4

class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'daniel'
        self.blockchain = Blockchain()
        if not self.blockchain.verify_chain():
            print('Invalid chain')
            exit(1)



    def get_transaction(self, receiver, amount):
        balance = self.blockchain.get_balance(self.id)
        if amount >= balance:
            print('Error not enought funds to complete transaction')
            return
        open_transaction = Transaction(amount, receiver, self.id)
        self.blockchain.add_transaction(open_transaction)

    def start_node(self):
        while True:
            print('Choose option:')
            print('1 - create a transaction')
            print('2 - display the blockchain')
            print('q - exit')
            print('m - mine')
            option = input(': ')
            if option == '1':
                receiver = input('Sending from ' + self.id + ' To: ')
                amount = float(input('Amount: '))
                self.get_transaction(receiver, amount)
            elif option == '2':
                print(self.blockchain)
            elif option == 'q':
                print('Exiting...')
                break
            elif option == 'm':
                self.blockchain.mine(self.id)
            else:
                print('Invalid option: ', option)
            if not self.blockchain.verify_chain():
                print('Invalid blockchain')
                break
            print('Balance of {}: {:10.2f} '.format(self.id, self.blockchain.get_balance(self.id)))


node = Node()
node.start_node()