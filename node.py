from dotenv import load_dotenv
load_dotenv()
import os
from flask import Flask, jsonify, redirect, url_for, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction

app = Flask(__name__)
CORS(app)
wallet = Wallet()
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'index.html'), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_dict = [block.__dict__.copy() for block in blockchain.chain]
    for cd in chain_dict:
        cd['transactions'] = [tx.__dict__ for tx in cd['transactions']]
    return jsonify(chain_dict), 200


@app.route('/mine', methods=['POST'])
def mine_block():
    block = blockchain.mine(wallet.getPublicKey())
    if block:
        block_dict = block.__dict__.copy()
        block_dict['transactions'] = [tx.__dict__ for tx in block_dict['transactions']]
        response = {
            'message': 'Mining was successfull',
            'block': block_dict,
            'balance': blockchain.get_balance(wallet.getPublicKey())
        }
        return response, 201
    else:
        err = {
            'message': 'Error mining block',
            'wallet': wallet.getPublicKey() != None
        }
        return err, 400


@app.route('/wallet', methods=['POST'])
def create_wallet():
    if not wallet.createKeys():
        response = {
            'message': 'Error creating wallet'
        }
        return response, 500
    response = {
        'message': 'Wallet successfully created',
        'private_key': wallet.getPrivateKey(),
        'public_key': wallet.getPublicKey(),
        'balance': blockchain.get_balance(wallet.getPublicKey())
    }
    return response, 201


@app.route('/wallet', methods=['GET'])
def load_wallet():
    if not wallet.loadKeys():
        response = {
            'message': 'Error loading keys'
        }
        return response, 500
    return redirect(url_for('get_balance'))


@app.route('/wallet/balance', methods=['GET'])
def get_balance():
    if not wallet.getPublicKey():
        response = {
            'message': 'Not a valid wallet'
        }
        return response, 400
    response = {
        'public_key': wallet.getPublicKey(),
        'private_key': wallet.getPrivateKey(),
        'balance': blockchain.get_balance(wallet.getPublicKey())
    }
    return response, 200


@app.route('/transaction', methods=['POST'])
def create_transaction():
    if not wallet.getPublicKey():
        response = {
            'message': 'Not a valid wallet'
        }
        return response, 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'must contain receiver and amount fields'
        }
        return response, 400
    
    required_fields = ['receiver', 'amount']
    if not all([field in values for field in required_fields]):
        response = {
            'message': 'must contain receiver and amount fields'
        }
        return response, 400
    receiver = values['receiver']
    try:
        amount = float(values['amount'])
    except ValueError:
        response = {
            'message': 'must contain a valid amount field'
        }
        return response, 400
    
    balance = blockchain.get_balance(wallet.getPublicKey())
    if amount >= balance:
        response = {
            'message': 'not enought funds to complete transaction'
        }
        return response, 400
    signature = wallet.sign_transaction(amount, receiver)
    open_transaction = Transaction(amount, receiver, wallet.getPublicKey(), signature)
    try:
        open_transaction.verify()
        blockchain.add_transaction(open_transaction)
    except AssertionError as err:
        return err, 500

    response = {
        'message': 'Transaction successfully added.',
        'transaction': open_transaction.__dict__,
        'balance': blockchain.get_balance(wallet.getPublicKey())
    }
    return response, 201


@app.route('/transactions', methods=['GET'])
def list_transactions():
    tx_dict = [tx.__dict__ for tx in blockchain.open_transactions]
    response = {
        'message': 'Found {} open transactions'.format(len(tx_dict)),
        'open_transactions': tx_dict
    }
    return response, 200


    

if __name__ == '__main__':
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = 5000
    app.run(host, port)