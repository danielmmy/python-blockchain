import hashlib
import collections
import json

from hash_util import compute_hash

MINE_REWARD = 10
DIFICULTY = 2
SAVE_FILE_PATH = 'data/blockchain.json'

blockchain = []
open_transactions = []
owner = 'daniel'
genesis_block = {
    'last_hash': '1',
    'index': len(blockchain),
    'transactions': [],
    'nonce': 0,
    'hash':'asd'
}


wallets = {owner}


blockchain.append(genesis_block)


def load_data():
    global blockchain
    global open_transactions
    try:
        with open(SAVE_FILE_PATH, 'r') as f:
            data = f.readlines()
            if data:
                blockchain = json.loads(data[0][:-1])
                open_transactions = json.loads(data[1])
    except:
        print('First time using the blockchain')

load_data()


def save_data():
    try:
        with open(SAVE_FILE_PATH, 'w') as f:
            f.write(json.dumps(blockchain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
    except:
        print('Error saving the blockchain')
        return 0


def get_balance(wallet):
    amount_sent = 0
    open_sent_transact = [open_tx['amount'] for open_tx in open_transactions if open_tx['sender'] == wallet]
    for value in open_sent_transact:
        amount_sent += value
    
    sent_transactions = [[transact['amount'] for transact in block['transactions']
                          if transact['sender'] == wallet] for block in blockchain]
    for transact in sent_transactions:
        for value in transact:
            amount_sent += value

    received_transactions = [[transact['amount'] for transact in block['transactions']
                          if transact['receiver'] == wallet] for block in blockchain]
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
    mine_block = {
        'sender': 'MINING',
        'receiver': owner,
        'amount': MINE_REWARD
    }
    mine_block_sorted = collections.OrderedDict(sorted(mine_block.items(), key=lambda t: t[0]))
    open_transactions_dup.append(mine_block_sorted)
    last_hash = compute_hash(blockchain[-1])
    block = {
        'last_hash': last_hash,
        'index': len(blockchain),
        'transactions': open_transactions_dup,
        'nonce': 0
    }
    while not proof_of_work(block, DIFICULTY):
        block['nonce'] += 1

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
    open_transaction={
        'sender': sender,
        'receiver': receiver,
        'amount': amount
    }
    open_transactions.append(collections.OrderedDict(sorted(open_transaction.items(), key=lambda t: t[0])))
    wallets.add(sender)
    wallets.add(receiver)
    save_data()


def verify_chain():
    for i in range(1, len(blockchain)):
        if blockchain[i]['last_hash'] != compute_hash(blockchain[i-1]):
            return False
        zeroes = '0' * DIFICULTY
        if compute_hash(blockchain[i])[:DIFICULTY] != zeroes:
            return False
    return True



while True:
    print('Choose option:')
    print('1 - create a transaction')
    print('2 - display the blockchain')
    print('3 - display open transactions')
    print('0 - exit')
    print('h - alter blockchain')
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
    elif option == '0':
        print('Exiting...')
        break
    elif option == 'h':
        index = int(input('Choose index to alter: '))
        if len(blockchain) > index:
            blockchain[index] = {
                'last_hash': 'dfadsfggdgadfad',
                'index': len(blockchain),
                'transactions': []
            }
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
