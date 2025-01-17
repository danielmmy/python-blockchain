import json
import hashlib

class BlockchainUtil:

    @staticmethod
    def compute_hash(block):
        return hashlib.sha256(json.dumps(block.__dict__, default=lambda o: o.__dict__).encode()).hexdigest()