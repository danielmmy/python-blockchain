from Crypto.PublicKey import RSA
import Crypto.Random
import binascii

class Wallet:
    def __init__(self):
        self.publicKey = None
        self.privateKey = None


    def createKeys(self):
        privateKey, publicKey = self.genKeys()
        self.publicKey = publicKey
        self.privateKey = privateKey


    def getPublicKey(self):
        if self.publicKey:
            return str(self.publicKey.export_key())
        else:
            return None


    def genKeys(self):
        key = RSA.generate(1024)
        private_key = key
        file_out = open("private.pem", "wb")
        file_out.write(private_key.export_key())
        file_out.close()

        public_key = key.publickey()
        file_out = open("public.pem", "wb")
        file_out.write(public_key.export_key())
        file_out.close()

        return private_key, public_key
        # return (binascii.hexlify(publicKey).decode('ascii'), binascii.hexlify(privateKey).decode('ascii'))


    def loadKeys(self):
        try:
            self.publicKey = RSA.import_key(open("public.pem").read())
            self.privateKey = RSA.import_key(open("private.pem").read())
        except (IOError, EOFError):
            print('No wallet found')
