import json
import hashlib

def compute_hash(block):
    return hashlib.sha256(json.dumps(block).encode()).hexdigest()