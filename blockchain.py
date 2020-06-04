from block import Block
from transaction import Transaction
from blockchain_util import BlockchainUtil
import pickle

DIFFICULTY = 2
MINE_REWARD = 10
SAVE_FILE_PATH = 'data/blockchain.data'


class Blockchain:
    def __init__(self):
        genesis_block = Block('1', 0, [])
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_data()

    def __repr__(self):
        chain_str = 'Chain: '
        open_tx_str = 'Open Transactions: '
        for block in self.chain:
            chain_str += str(block)
        for tx in self.open_transactions:
            open_tx_str += str(tx) + '\n'
        return chain_str + ('-'*30)+'\n'+open_tx_str

    def load_data(self):
        try:
            with open(SAVE_FILE_PATH, 'rb') as f:
                blockchain = pickle.loads(f.read())
                self.chain = blockchain.chain
                self.open_transactions = blockchain.open_transactions
        except IOError:
            pass

    def save_data(self):
        try:
            with open(SAVE_FILE_PATH, 'wb') as f:
                f.write(pickle.dumps(self))
        except IOError:
            print('Error saving the blockchain')
            pass

    def get_length(self):
        return len(self.chain)


    def get_open_transactions(self):
        return self.open_transactions


    def add_transaction(self, transaction):
        self.open_transactions.append(transaction)
        self.save_data()


    def get_last_chain(self):
        return self.chain[-1]


    def verify_chain(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].last_hash != BlockchainUtil.compute_hash(self.chain[i-1]):
                return False
            zeroes = '0' * DIFFICULTY
            if BlockchainUtil.compute_hash(self.chain[i])[:DIFFICULTY] != zeroes:
                return False
        return True


    def get_balance(self, wallet):
        amount_sent = 0
        open_sent_transact = [
            open_tx.amount for open_tx in self.open_transactions if open_tx.sender == wallet]
        for value in open_sent_transact:
            amount_sent += value

        sent_transactions = [[transact.amount for transact in block.transactions
                              if transact.sender == wallet] for block in self.chain]
        for transact in sent_transactions:
            for value in transact:
                amount_sent += value

        received_transactions = [[transact.amount for transact in block.transactions
                                  if transact.receiver == wallet] for block in self.chain]
        amount_received = 0
        for transact in received_transactions:
            for value in transact:
                amount_received += value

        return amount_received - amount_sent


    def proof_of_work(self, block):
        hash = BlockchainUtil.compute_hash(block)
        zeroes = '0' * DIFFICULTY
        return hash[:DIFFICULTY] == zeroes


    def mine(self, owner):
        open_transactions_dup = self.open_transactions[:]
        mine_transaction = Transaction(MINE_REWARD, owner, 'MINING')
        open_transactions_dup.append(mine_transaction)
        last_hash = BlockchainUtil.compute_hash(self.get_last_chain())
        block = Block(
            last_hash,
            self.get_length(),
            open_transactions_dup
        )
        while not self.proof_of_work(block):
            block.nonce += 1

        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
