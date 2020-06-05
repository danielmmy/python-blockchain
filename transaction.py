from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii

class Transaction:
    def __init__(self, amount, receiver, sender, signature=None):
        self.amount = amount
        self.receiver = receiver
        self.sender = sender
        self.signature = signature

    
    def __repr__(self):
        return 'Sender: {}, Receiver: {}, Amount: {}, Signature: {}'.format(self.sender, self.receiver, self.amount, self.signature)

    
    def verify(self):
        verifier = PKCS1_v1_5.new(RSA.import_key(binascii.unhexlify(self.sender)))
        tx_str = '{}{}{}'.format(str(self.amount), str(self.receiver), str(self.sender))
        hash = SHA256.new(tx_str.encode())
        is_valid= verifier.verify(hash, binascii.unhexlify(self.signature))
        if not is_valid:
            raise AssertionError('Transaction does not verify')