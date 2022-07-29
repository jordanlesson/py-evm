from eth.chains.base import MiningChain
from eth_typing import Address
from eth.db.atomic import AtomicDB
from eth_keys import keys
from eth.tools.builder.chain.builders import disable_pow_check
from eth.constants import GENESIS_BLOCK_NUMBER
from eth.vm.forks.lynx import LynxVM


SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())
RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

GENESIS_PARAMS = {'gas_limit': 3141592, 'timestamp': 1514764800,}

GENESIS_STATE = {
    SENDER_ADDRESS : {
        'balance': 69,
        'nonce': 0,
        'code': b'',
        'storage': {},
    }
}

def test_blockchain():
    blockchain_config = MiningChain.configure(
                __name__='LynxChain',
                vm_configuration=((GENESIS_BLOCK_NUMBER, LynxVM),
            )   
        )
        
    blockchain : MiningChain = blockchain_config.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE) # pylint: disable=no-member
    disable_pow_check(blockchain)

    genesis = blockchain.get_canonical_block_by_number(GENESIS_BLOCK_NUMBER)

    tx = blockchain.create_unsigned_transaction(
            nonce=0,
            gas_price=0,
            gas=100000,
            to=RECEIVER,
            value=20,
            data=b'Aliens are real!',
        )

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    blockchain.apply_transaction(signed_tx)

    blockchain.set_header_timestamp(genesis.header.timestamp + 1)

    block_result = blockchain.get_vm().finalize_block(blockchain.get_block())
    block = block_result.block

    blockchain.persist_block(block, perform_validation=True)

    print(blockchain.get_canonical_head().as_dict())

if __name__ == '__main__':
    test_blockchain()