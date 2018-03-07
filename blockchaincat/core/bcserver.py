import json
from uuid import uuid4
from flask import Flask, jsonify, request
import core.blockchaincat;
import requests

# 初始化节点
app = Flask(__name__)

node_identifier="zhangxs";    #生成唯一ID，可以用str(uuid4()).replace('-', '')
blockchain = core.blockchaincat.Blockchaincat();   #初始化


# 挖矿接口
@app.route('/mine', methods=['GET','POST'])
def mine():

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 给工作量证明的节点提供奖励.发送者为 "catGod" 表明是新挖出的币
    blockchain.new_transaction(
        sender="catGod",
        recipient=node_identifier,
        amount=1,
        msg="catGod give "+node_identifier+" total 1 catcoin",
    )

    # 造一个新的区块，并且填入到链里面
    block = blockchain.new_block(proof, None)

    # 节点同步（自己有了新的块，通知其他节点更新）
    # for node in blockchain.nodes:
    #     response = requests.get(f'http://{node}/nodes/resolve')

    responseend = {
        'message': "this is a block "+str(block['index']),
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(responseend), 200

#交易接口
@app.route('/trans', methods=['GET','POST'])
def new_transaction():
    valuesstr=request.data
    print(valuesstr);
    values = json.loads(valuesstr)
    # 检查POST数据
    # 数据格式为{"sender:"AAA","recipient":"BBB","amount",1,"msg","AAAA 给 BBB 共 1 猫币"}
    required = ['sender', 'recipient', 'amount', 'msg']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 创建一个交易
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'],values['msg'])

    print("new_transaction over,start sync");
    # 交易通知
    for node in blockchain.nodes:
        response = requests.post(f'http://{node}/trans_sync',data=valuesstr)

    responseend = {'message': f'will be add in block {index}'}
    return jsonify(responseend), 200

#交易同步接口
@app.route('/trans_sync', methods=['GET','POST'])
def new_transaction_sync():
    valuesstr=request.data
    print(valuesstr);
    values = json.loads(valuesstr)
    # 检查POST数据
    # 数据格式为{"sender:"AAA","recipient":"BBB","amount",1,"msg","AAAA 给 BBB 共 1 猫币"}
    required = ['sender', 'recipient', 'amount', 'msg']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 创建一个交易
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'],values['msg'])

    responseend = {'message': f'will be sync in block {index}'}
    return jsonify(responseend), 200

#显示整个区块链
@app.route('/chain', methods=['GET','POST'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# 显示注册的节点
@app.route('/nodes', methods=['GET','POST'])
def full_nodes():

    if len(blockchain.nodes)> 0:
        nodelist = []
        for node in blockchain.nodes:
            print(node);
            nodelist.append(node);

        response = {
            'nodes': nodelist,
        }
    else:
        response = {
            'nodes': '',
        }

    return jsonify(response), 200


# 未写入区块的交易
@app.route('/buftranslist', methods=['GET','POST'])
def full_buftrans():
    response = {
        'transactions': blockchain.current_transactions
    }
    return jsonify(response), 200

#注册一个节点
@app.route('/nodes/register', methods=['GET','POST'])
def register_nodes():
    valuesstr = request.data
    values = json.loads(valuesstr)
    # 检查POST数据
    # 数据格式为{"nodes":["http://localhost:5000","http://localhost:5001","http://localhost:5002"]}
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: nodes is null", 400

    for node in nodes: 
        blockchain.register_node(node)

    response = {
        'message': 'new node is added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200

#区块链节点间同步（共识算法）
@app.route('/nodes/resolve', methods=['GET','POST'])
def consensus():
    print("start resolve");
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'my blockchain had been replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'my blockchain had been keep',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
