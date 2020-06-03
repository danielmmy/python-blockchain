class Transaction:
    def __init__(self, amount, receiver, sender):
        self.amount = amount
        self.receiver = receiver
        self.sender = sender

    
    def __repr__(self):
        return 'Sender: {}, Receiver: {}, Amount: {}'.format(self.sender, self.receiver, self.amount)