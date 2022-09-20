from eth_typing import Address
from eth.db.atomic import AtomicDB
from eth_keys import keys
from eth.constants import GENESIS_BLOCK_NUMBER, CREATE_CONTRACT_ADDRESS
from eth.vm.forks.lynx import LynxVM
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.chains.lynx import LynxChain, LYNX_VM_CONFIGURATION


SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())
RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

GENESIS_PARAMS = {'timestamp': 1514764800}

GENESIS_STATE = {
    SENDER_ADDRESS : {
        'balance': 69,
        'nonce': 0,
        'code': b'',
        'storage': {},
    }
}

def test_blockchain():
    blockchain_config : LynxChain = LynxChain.configure(
                __name__='LynxChain',
                vm_configuration=LYNX_VM_CONFIGURATION,
            )   
    print(type(blockchain_config))
        
    blockchain : LynxChain = blockchain_config.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE)

    genesis : LynxBlock = blockchain.get_canonical_block_by_number(block_number=0)

    vm = blockchain.get_vm()

    tx = vm.create_unsigned_transaction(
            nonce=1,
            gas_price=0,
            gas=1000000,
            to=CREATE_CONTRACT_ADDRESS,
            value=0,
            data=b'',
        )

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    blockchain.apply_transaction(signed_tx)

    block : LynxBlock = blockchain.forge_block()

    block.get_receipts(chaindb=blockchain.chaindb)

if __name__ == '__main__':
    test_blockchain()
