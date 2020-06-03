import hashlib
import collections
import pickle
from block import Block
from transaction import Transaction

from hash_util import compute_hash

MINE_REWARD = 10
DIFICULTY = 2
SAVE_FILE_PATH = 'data/blockchain.data'

blockchain = []
open_transactions = []
owner = 'daniel'


wallets = {owner}


def load_data():
    global blockchain
    global open_transactions
    try:
        with open(SAVE_FILE_PATH, 'rb') as f:
            data = f.read()
            if data:
                saved_data = pickle.loads(data)
                blockchain = saved_data['blockchain']
                open_transactions = saved_data['open_transactions']
            else:
                raise IOError
    except IOError:
        print('First time using the blockchain')
        genesis_block = Block(
            '1',
            len(blockchain),
            [],
        )
        blockchain.append(genesis_block)


load_data()


def save_data():
    try:
        with open(SAVE_FILE_PATH, 'wb') as f:
            saved_data = {
                'blockchain': blockchain,
                'open_transactions': open_transactions
            }
            f.write(pickle.dumps(saved_data))
    except IOError:
        print('Error saving the blockchain')
        return 0


def get_balance(wallet):
    amount_sent = 0
    open_sent_transact = [open_tx.amount for open_tx in open_transactions if open_tx.sender == wallet]
    for value in open_sent_transact:
        amount_sent += value
    
    sent_transactions = [[transact.amount for transact in block.transactions
                          if transact.sender == wallet] for block in blockchain]
    for transact in sent_transactions:
        for value in transact:
            amount_sent += value

    received_transactions = [[transact.amount for transact in block.transactions
                          if transact.receiver == wallet] for block in blockchain]
    amount_received = 0
    for transact in received_transactions:
        for value in transact:
            amount_received += value


    return amount_received - amount_sent


def proof_of_work(block, difficulty):
    hash = compute_hash(block)
    zeroes = '0' * difficulty
    return hash[:difficulty] == zeroes

def mine():
    global open_transactions
    open_transactions_dup = open_transactions[:]
    mine_transaction = Transaction(MINE_REWARD, owner, 'MINING')
    open_transactions_dup.append(mine_transaction)
    last_hash = compute_hash(blockchain[-1])
    block = Block(
        last_hash,
        len(blockchain),
        open_transactions_dup
    )
    while not proof_of_work(block, DIFICULTY):
        block.nonce += 1

    blockchain.append(block)
    open_transactions = []
    save_data()



def add_value(val, last_chain=[1]):
    blockchain.append([last_chain, val])


def get_transaction(sender, receiver, amount):
    balance = get_balance(sender)
    if amount >= balance:
        print('Error not enought funds to complete transaction')
        return
    open_transaction = Transaction(amount, receiver, sender)
    open_transactions.append(open_transaction)
    wallets.add(sender)
    wallets.add(receiver)
    save_data()


def verify_chain():
    for i in range(1, len(blockchain)):
        if blockchain[i].last_hash != compute_hash(blockchain[i-1]):
            return False
        zeroes = '0' * DIFICULTY
        if compute_hash(blockchain[i])[:DIFICULTY] != zeroes:
            return False
    return True

if not verify_chain():
    print('Invalid chain')
    exit(1)



while True:
    print('Choose option:')
    print('1 - create a transaction')
    print('2 - display the blockchain')
    print('3 - display open transactions')
    print('q - exit')
    print('m - mine')
    print('u - display user\'s wallets')
    option = input(': ')
    if option == '1':
        receiver = input('Sending from ' + owner + ' To: ')
        amount = float(input('Amount: '))
        get_transaction(owner, receiver, amount)
        print(open_transactions)
    elif option == '2':
        print(blockchain)
    elif option == '3':
        print(open_transactions)
    elif option == 'q':
        print('Exiting...')
        break
    elif option == 'm':
        mine()
    elif option == 'u':
        print(wallets)
    else:
        print('Invalid option: ', option)
    if not verify_chain():
        print('Invalid blockchain')
        break
    print('Balance of {}: {:10.2f} '.format(owner, get_balance(owner)))
