import hashlib
import json
from time import time
import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import requests


class Blockchaincat:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        # 创建创世块
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address: str) -> None:        # 注册一个节点
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain: List[Dict[str, Any]]) -> bool:
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}{block}')
            if block['previous_hash'] != self.hash(last_block):# 检查区块的hash是否正确
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):# 检查工作量证明(POW)是否正确
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool: #共识算法解决冲突:使用网络中最长的链.如果链被取代返回 True, 否则为False
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain) #自己的长度

        # 遍历整个节点网络，看看谁最长
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain): #计算链长，检查有效性，记录最长的链
                    max_length = length
                    new_chain = chain

        if new_chain: #把自己的链替换成最长的
            self.chain = new_chain
            self.current_transactions = []
            return True

        return False

    def new_block(self, proof: int, previous_hash: Optional[str]) -> Dict[str, Any]:  #生成新块,proof: 校验参数,previous_hash:上一个的hash
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int, msg: str) -> int:
        # 生成新交易信息，信息将加入到下一个待挖的区块中
        # :param sender: 发送人
        # :param recipient: 接受人
        # :param amount: 数量
        # :param msg: 交易信息
        # :param time: 交易时间
        # :return: 区块位置
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'msg': msg,
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }) 
        return self.last_block['index'] + 1

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    @staticmethod
    def hash(block: Dict[str, Any]) -> str: #生成块的 SHA-256 hash值
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        # 简单的工作量证明:
        #  - 查找一个 p' 使得 hash(pp') 以4个0开头
        #  - p 是上一个块的证明,  p' 是当前的证明
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头
        :param last_proof: Previous Proof
        :param proof: Current Proof
        :return: True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"