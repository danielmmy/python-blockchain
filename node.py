from dotenv import load_dotenv
load_dotenv()
import os
import pickle
from flask import Flask, jsonify, redirect, url_for, request, send_from_directory
from flask_cors import CORS
import requests
from argparse import ArgumentParser
from wallet import Wallet
from blockchain import Blockchain
from block import Block
from transaction import Transaction

# define server variables
host = os.getenv('HOST')
port = os.getenv('PORT')
if not host:
    host = '0.0.0.0'
if not port:
    port = 5000

parser= ArgumentParser()
parser.add_argument('-p', '--port')
args = parser.parse_args()
if args.port:
    port = args.port
#end define server variable

app = Flask(__name__)
CORS(app)
wallet = Wallet('data/private_{}.pem'.format(str(port)), 'data/public_{}.pem'.format(str(port)))
blockchain = Blockchain('data/blockchain_{}.data'.format(str(port)))

# Node peer set routines
SAVE_PEER_PATH = 'data/peers_{}.data'.format(str(port))
peer_set = set()


def add_peer(url):
    peer_set.add(url)
    return save_peer_set()


def discard_peer(url):
    peer_set.discard(url)
    return save_peer_set()


def get_peer_set():
    return peer_set.copy()


def save_peer_set():
    try:
        with open(SAVE_PEER_PATH, 'wb') as f:
                f.write(pickle.dumps(peer_set))
                return True
    except IOError:
        print('Error saving the peer set')
        return False
        

def load_peer_set():
    global peer_set
    try:
        with open(SAVE_PEER_PATH, 'rb') as f:
            peer_set = pickle.loads(f.read())
    except IOError:
        pass
load_peer_set()
# End node peer set routines


# Routes
@app.route('/nodes', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'must contain node url'
        }
        return response, 400
    if not values['url']:
        response = {
            'message': 'must contain node url'
        }
        return response, 400
    
    if not add_peer(values['url']):
        response = {
            'message': 'Error adding node to peers'
        }
        return response, 500

    response = {
        'message': 'Node successfully added to peers',
        'nodes': list(get_peer_set())
    }
    return response, 201


# Routes
@app.route('/nodes/<url>', methods=['DELETE'])
def delete_node(url):
    if (not url) or (url == ''):
        response = {
            'message': 'must contain node url'
        }
        return response, 400
       
    if not discard_peer(url):
        response = {
            'message': 'Error deleting node from peers'
        }
        return response, 500

    response = {
        'message': 'Node successfully deleted from peers',
        'nodes': list(get_peer_set())
    }
    return response, 201



@app.route('/nodes', methods=['GET'])
def  list_nodes():
    response = {
        'message': 'Found {} peer nodes'.format(len(get_peer_set())),
        'nodes': list(get_peer_set())
    }
    return response, 200



@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'index.html'), 200


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html'), 200


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
        original_url = 'http://localhost:{}/broadcast-block'.format(port)
        received = {original_url}
        should_send_set = set()
        for peer in peer_set:
            url = 'http://{}/broadcast-block'.format(peer)
            received.add(url)
            should_send_set.add(url)

        for url in should_send_set:
            #dont send itself
            if url == original_url:
                continue
            try:
                response = requests.post(url, json={
                    'block': block_dict,
                    'received': list(received)
                })
                if response.status_code == 400 or response.status_code == 500:
                    print('Transaction rejected, needs resolving.')
                if response.status_code == 406:
                    print('Longer chain found')
            except ConnectionError:
                response = {
                    'message': 'Errro broadcasting to {}'.format(url)
                }
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


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    this_url= 'http://{}/broadcast-block'.format(port)
    values = request.get_json()

    if not values:
        response = {
            'message': 'No data received'
        }
        return response, 400
    required_fields = ['block', 'received']
    if not all([field in values for field in required_fields]):
        response = {
            'message': 'must contain block'
        }
        return response, 400

    received = set(values['received'])

    if this_url in received:
        response = {
            'message': 'Node has already received the block'
        }
        return response, 200

    block_dict = values['block']
    current_index = blockchain.get_last_chain().index + 1
    if block_dict['index'] == current_index:
        response = {
            'message': 'Longer chain found',
            'blocks': blockchain.get_chain_dict(block_dict['index'])
        }
        return response, 406
    tx_list = []
    for tx in block_dict['transactions']:
        tx_list.append(Transaction(float(tx['amount']), tx['receiver'], tx['sender'], tx['signature']))
    block = Block(block_dict['last_hash'], int(block_dict['index']), tx_list, block_dict['nonce'])

    if not blockchain.add_block(block):
        response = {
            'message': 'Broadcasted block not added'
        }
        return response, 500
    response = {
        'message': 'Broadcasted block added'
    }
    should_send_set = set()
    print('received:', received)
    for peer in peer_set:
        url = 'http://{}/broadcast-block'.format(peer)
        if (not url in received) or url == this_url:
            received.add(url)
            should_send_set.add(url)
    print('Should send:', should_send_set)
    print('received:', received)
    for url in should_send_set:
        # IF NOT ITSELF OR ORIGIN BROADCAST MESSAGE
        if url != this_url:
            try:
                response = requests.post(url, json={
                    'block': values['block'],
                    'received': list(received)
                })
                if response.status_code == 400 or response.status_code == 500:
                    print('Transaction rejected, needs resolving.')
            except ConnectionError:
                continue
    return response, 201



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
        original_url = 'http://localhost:{}/broadcast-transaction'.format(port)
        received = {original_url}
        should_send_set = set()
        for peer in peer_set:
            url = 'http://{}/broadcast-transaction'.format(peer)
            received.add(url)
            should_send_set.add(url)

        for url in should_send_set:
            #dont send itself
            if url == original_url:
                continue
            try:
                response = requests.post(url, json={
                    'transaction': open_transaction.__dict__,
                    'received': list(received)
                })
                if response.status_code == 400 or response.status_code == 500:
                    print('Transaction rejected, needs resolving.')
            except ConnectionError:
                response = {
                    'message': 'Errro broadcasting to {}'.format(url)
                }
                return response, 421
    except AssertionError as err:
        return err, 500

    response = {
        'message': 'Transaction successfully added.',
        'transaction': open_transaction.__dict__,
        'balance': blockchain.get_balance(wallet.getPublicKey())
    }
    return response, 201


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    this_url= 'http://{}/broadcast-transaction'.format(port)
    values = request.get_json()

    if not values:
        response = {
            'message': 'No data received'
        }
        return response, 400
    required_fields = ['transaction', 'received']
    if not all([field in values for field in required_fields]):
        response = {
            'message': 'must contain transaction'
        }
        return response, 400

    received = set(values['received'])

    if this_url in received:
        response = {
            'message': 'Node has already received the transaction'
        }
        return response, 200

    tx_dict = values['transaction']
    transaction = Transaction(tx_dict['amount'], tx_dict['receiver'], tx_dict['sender'], tx_dict['signature'])
    try:
        transaction.verify()
        blockchain.add_transaction(transaction)
        response = {
            'message': 'Broadcasted transaction added'
        }
        should_send_set = set()
        print('received:', received)
        for peer in peer_set:
            url = 'http://{}/broadcast-transaction'.format(peer)
            if (not url in received) or url == this_url:
                received.add(url)
                should_send_set.add(url)
        print('Should send:', should_send_set)
        print('received:', received)
        for url in should_send_set:
            # IF NOT ITSELF OR ORIGIN BROADCAST MESSAGE
            if url != this_url:
                try:
                    response = requests.post(url, json={
                        'transaction': transaction.__dict__,
                        'received': list(received)
                    })
                    if response.status_code == 400 or response.status_code == 500:
                        print('Transaction rejected, needs resolving.')
                except ConnectionError:
                    continue
        return response, 201
    except AssertionError as err:
        return err, 500



@app.route('/transactions', methods=['GET'])
def list_transactions():
    tx_dict = [tx.__dict__ for tx in blockchain.open_transactions]
    response = {
        'message': 'Found {} open transactions'.format(len(tx_dict)),
        'open_transactions': tx_dict
    }
    return response, 200


#End routes


# Start server
if __name__ == '__main__':
    app.run(host, port)