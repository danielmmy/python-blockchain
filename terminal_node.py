from block import Block
from blockchain import Blockchain
from transaction import Transaction
from uuid import uuid4
from wallet import Wallet

class TerminalNode:
    def __init__(self):
        # self.id = str(uuid4())
        self.wallet = Wallet()
        self.blockchain = Blockchain()
        if not self.blockchain.verify_chain():
            print('Invalid chain')
            exit(1)



    def get_transaction(self):
        receiver = input('Sending from ' + self.wallet.getPublicKey() + ' To: ')
        amount = float(input('Amount: '))
        balance = self.blockchain.get_balance(self.wallet.getPublicKey())
        if amount >= balance:
            print('Error not enought funds to complete transaction')
            return
        signature = self.wallet.sign_transaction(amount, receiver)
        open_transaction = Transaction(amount, receiver, self.wallet.getPublicKey(), signature)
        try:
            open_transaction.verify()
            self.blockchain.add_transaction(open_transaction)
        except AssertionError as err:
            print(err)

    def start_node(self):
        while True:
            print('Choose option:')
            print('1 - create a transaction')
            print('2 - display the blockchain')
            print('3 - create new wallet')
            print('4 - load wallet')
            print('q - exit')
            print('m - mine')
            option = input(': ')
            if (not self.wallet.getPublicKey()) and option != '3' and option != '4' and option != 'q':
                print('Error: needs a wallet first.')
                continue
            if option == '1':
                self.get_transaction()
            elif option == '2':
                print(self.blockchain)
            elif option == '3':
                self.wallet.createKeys()
            elif option == '4':
                self.wallet.loadKeys()
            elif option == 'q':
                print('Exiting...')
                break
            elif option == 'm':
                self.blockchain.mine(self.wallet.getPublicKey())
            else:
                print('Invalid option: ', option)
            if not self.blockchain.verify_chain():
                print('Invalid blockchain')
                break
            print('Balance of {}: {:10.2f} '.format(self.wallet.getPublicKey(), self.blockchain.get_balance(self.wallet.getPublicKey())))


terminalNode = TerminalNode()
terminalNode.start_node()