class Block:
    def __init__(self, last_hash, index, transactions, nonce = 0 ):
        self.last_hash = last_hash
        self.index = index
        self.transactions = transactions
        self.nonce = nonce


    def __repr__(self):
        return 'index: {}\nLast Hash: {}\nTransactions: {}\n'.format(self.index, self.last_hash, self.transactions)