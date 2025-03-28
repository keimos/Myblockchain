from blockchain import Blockchain
from uuid import uuid4
from flask import Flask, jsonify, request
from flaskrun import flaskrun

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We will run the proof of work algorithm to get the next proof..
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender = "0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new block by adding it to the chain.
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Handle creating a new transaction."""
    values = request.get_json()

    # Check that the required fields are in the POSTed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values: {k}', 400

    # Create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_all_nodes():
    """Retrieve all registed nodes."""
    response = {
        'message': 'All registered nodes',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if not nodes:
        return jsonify({'error': 'Please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/deregister', methods=['POST'])
def deregister_nodes():
    """Deregisterd existing nodes."""
    values = request.get_json()

    nodes = values.get('nodes')
    if not nodes:
        return jsonify({'error': 'Error, please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchain.deregister_node(node)

    response = {
        'message': 'Nodes de-registered',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods = ['GET'])
def resolve_conflict():
    """Resolve blockchain conflicts."""
    replaced = blockchain.resolve_conflicts()

    response = {
        'message': 'Our chain got replaced' if replaced else 'Our chain is authoritative',
        'chain': blockchain.chain
    }
    return jsonify(response), 200

if __name__ == '__main__':
    # Run the Flask app
    flaskrun(app)
