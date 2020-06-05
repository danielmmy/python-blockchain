from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Random
from Crypto.Hash import SHA256
import binascii

class Wallet:
    def __init__(self):
        self.publicKey = None
        self.privateKey = None


    def createKeys(self):
        privateKey, publicKey = self.genKeys()
        self.publicKey = publicKey
        self.privateKey = privateKey

        if privateKey and publicKey:
            return True
        return False


    def getPublicKey(self):
        if self.publicKey:
            return binascii.hexlify(self.publicKey.export_key()).decode()
        else:
            return None


    def getPrivateKey(self):
        if self.privateKey:
            return binascii.hexlify(self.privateKey.export_key()).decode()
        else:
            return None


    def genKeys(self):
        private_key = None
        public_key = None
        try:
            key = RSA.generate(1024)
            private_key = key
            file_out = open("private.pem", "wb")
            file_out.write(private_key.export_key())
            file_out.close()

            public_key = key.publickey()
            file_out = open("public.pem", "wb")
            file_out.write(public_key.export_key())
            file_out.close()
        except:
            pass


        return private_key, public_key
        # return (binascii.hexlify(publicKey).decode('ascii'), binascii.hexlify(privateKey).decode('ascii'))


    def loadKeys(self):
        try:
            self.publicKey = RSA.import_key(open("public.pem").read())
            self.privateKey = RSA.import_key(open("private.pem").read())
            return True
        except (IOError, EOFError):
            print('No wallet found')
            return False


    def sign_transaction(self, amount, receiver):
        signer = PKCS1_v1_5.new(self.privateKey)
        tx_str = '{}{}{}'.format(str(amount), str(receiver), self.getPublicKey())
        hash = SHA256.new(tx_str.encode())
        signature = signer.sign(hash)
        return binascii.hexlify(signature).decode('ascii')
        


