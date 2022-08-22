from abc import ABC
from typing import (
    Type, 
    cast,
    List,
    Tuple,
    Sequence
)
from eth.abc import (
    BlockHeaderSedesAPI,
    TransactionBuilderAPI, 
    BlockHeaderAPI,
    MiningHeaderAPI,
    ChainDatabaseAPI,
    SignedTransactionAPI,
    ReceiptAPI,
    ReceiptBuilderAPI,
)
from eth.rlp.blocks import (
    BaseBlock,
)
from eth.vm.forks.london.transactions import LondonReceiptBuilder
from eth_bloom import (
    BloomFilter,
)
from eth_utils import (
    encode_hex,
)
from trie.exceptions import (
    MissingTrieNode,
)
from eth._utils.headers import (
    new_timestamp_from_parent,
)
from eth.exceptions import (
    BlockNotFound,
    HeaderNotFound,
)
from eth_hash.auto import keccak
import rlp
from rlp.sedes import (
    Binary,
    CountableList,
    big_endian_int,
    binary
)
from eth.rlp.sedes import (
    address,
    hash32,
    trie_root,
    uint256,
)
from eth.rlp.headers import (
    BlockHeader,
)
from eth_typing import (
    BlockNumber,
)
from eth_typing.evm import (
    Address,
    Hash32
)
from eth.constants import (
    ZERO_ADDRESS,
    ZERO_HASH32,
    EMPTY_UNCLE_HASH,
    GENESIS_NONCE,
    GENESIS_PARENT_HASH,
    BLANK_ROOT_HASH,
)

from .transactions import LynxTransactionBuilder

UNMINED_LYNX_HEADER_FIELDS = [
    ('parent_hash', hash32),
    # ('uncles_hash', hash32),
    ('coinbase', address),
    ('state_root', trie_root),
    ('transaction_root', trie_root),
    ('receipt_root', trie_root),
    ('bloom', uint256),
    ('block_number', big_endian_int),
    # ('gas_limit', big_endian_int),
    ('gas_used', big_endian_int),
    ('timestamp', big_endian_int),
    ('extra_data', binary),
    ('epoch', uint256),
    ('slot', uint256),
    # ('base_fee_per_gas', big_endian_int),
]

class LynxMiningHeader(rlp.Serializable, MiningHeaderAPI):
    fields = UNMINED_LYNX_HEADER_FIELDS


class LynxBlockHeader(rlp.Serializable, BlockHeaderAPI):
    fields = UNMINED_LYNX_HEADER_FIELDS[:-1] + [
        # ('mix_hash', binary),
        # ('nonce', Binary(8, allow_empty=True)),
    ] + UNMINED_LYNX_HEADER_FIELDS[-1:]

    def __init__(self,
                 block_number: BlockNumber,
                #  gas_limit: int,
                 timestamp: int = None,
                 coinbase: Address = ZERO_ADDRESS,
                 parent_hash: Hash32 = ZERO_HASH32,
                #  uncles_hash: Hash32 = EMPTY_UNCLE_HASH,
                 state_root: Hash32 = BLANK_ROOT_HASH,
                 transaction_root: Hash32 = BLANK_ROOT_HASH,
                 receipt_root: Hash32 = BLANK_ROOT_HASH,
                 bloom: int = 0,
                 gas_used: int = 0,
                 extra_data: bytes = b'',
                #  nonce: bytes = GENESIS_NONCE,
                #  mix_hash: Hash32 = ZERO_HASH32,
                #  base_fee_per_gas: int = 0,
                #  slot_leader : Address = ZERO_ADDRESS,
                 epoch : int = 1,
                 slot : int = 1,
                 ) -> None:
        if timestamp is None:
            if parent_hash == ZERO_HASH32:
                timestamp = new_timestamp_from_parent(None)
            else:
                # without access to the parent header, we cannot select a new timestamp correctly
                raise ValueError("Must set timestamp explicitly if this is not a genesis header")
        super().__init__(
            parent_hash=parent_hash,
            # uncles_hash=uncles_hash,
            coinbase=coinbase,
            state_root=state_root,
            transaction_root=transaction_root,
            receipt_root=receipt_root,
            bloom=bloom,
            block_number=block_number,
            # gas_limit=gas_limit,
            gas_used=gas_used,
            timestamp=timestamp,
            extra_data=extra_data,
            # mix_hash=mix_hash,
            # nonce=nonce,
            epoch=epoch,
            slot=slot,
            # base_fee_per_gas=base_fee_per_gas,
        )
        # self.slot : int = slot
        # self.slot_leader : Address = slot_leader
        

    def __str__(self) -> str:
        return f'<LynxBlockHeader #{self.block_number} {self.hash.hex()[2:10]}>'
    
    _hash = None 

    @property
    def hash(self) -> Hash32:
        if self._hash is None:
            self._hash = keccak(rlp.encode(self))
        return cast(Hash32, self._hash)

    @property
    def mining_hash(self) -> Hash32:
        non_pow_fields = self[:-3] + self[-1:]
        result = keccak(rlp.encode(non_pow_fields, LynxMiningHeader))
        return cast(Hash32, result)

    @property
    def hex_hash(self) -> str:
        return encode_hex(self.hash)

    @property
    def is_genesis(self) -> bool:
        # if removing the block_number == 0 test, consider the validation consequences.
        # validate_header stops trying to check the current header against a parent header.
        # Can someone trick us into following a high difficulty header with genesis parent hash?
        return self.parent_hash == GENESIS_PARENT_HASH and self.block_number == 0

    @property
    def base_fee_per_gas(self) -> int:
        raise AttributeError("Base fee per gas not available until London fork")

    @property
    def epoch(self) -> int:
        return self.epoch

    @property
    def slot(self) -> int:
        return self.slot
    
    
class LynxBackwardsHeader(BlockHeaderSedesAPI):
    """
    An rlp sedes class for block headers.

    It can serialize and deserialize *both* Lynx and pre-Lynx headers.
    """

    @classmethod
    def serialize(cls, obj: BlockHeaderAPI) -> List[bytes]:
        return obj.serialize(obj)

    @classmethod
    def deserialize(cls, encoded: List[bytes]) -> LynxBlockHeader:
        num_fields = len(encoded)
        # if num_fields == 16:
        return LynxBlockHeader.deserialize(encoded)
        # elif num_fields == 15:
        #     return BlockHeader.deserialize(encoded)
        # else:
        #     raise ValueError(
        #         "Lynx & earlier can only handle headers of 15 or 16 fields. "
        #         f"Got {num_fields} in {encoded!r}"
        #     )

class LynxBlock(BaseBlock):
    transaction_builder = LynxTransactionBuilder
    receipt_builder: Type[ReceiptBuilderAPI] = LondonReceiptBuilder
    fields = [
        ('header', BlockHeader),
        ('transactions', CountableList(transaction_builder)),
        # ('uncles', CountableList(BlockHeader))
    ]

    bloom_filter = None

    def __init__(self,
                 header: BlockHeaderAPI,
                 transactions: Sequence[SignedTransactionAPI] = None,
                #  uncles: Sequence[BlockHeaderAPI] = None
                 ) -> None:
        if transactions is None:
            transactions = []
        # if uncles is None:
        #     uncles = []

        self.bloom_filter = BloomFilter(header.bloom)

        super().__init__(
            header=header,
            transactions=transactions,
            # uncles=uncles,
        )
        # TODO: should perform block validation at this point?

    #
    # Helpers
    #
    @property
    def number(self) -> BlockNumber:
        return self.header.block_number

    @property
    def hash(self) -> Hash32:
        return self.header.hash

    #
    # Transaction class for this block class
    #
    @classmethod
    def get_transaction_builder(cls) -> Type[TransactionBuilderAPI]:
        return cls.transaction_builder

    @classmethod
    def get_receipt_builder(cls) -> Type[ReceiptBuilderAPI]:
        return cls.receipt_builder

    #
    # Receipts API
    #
    def get_receipts(self, chaindb: ChainDatabaseAPI) -> Tuple[ReceiptAPI, ...]:
        return chaindb.get_receipts(self.header, self.get_receipt_builder())

    #
    # Header API
    #
    @classmethod
    def from_header(cls, header: BlockHeaderAPI, chaindb: ChainDatabaseAPI) -> "LynxBlock":
        """
        Returns the block denoted by the given block header.

        :raise eth.exceptions.BlockNotFound: if transactions or uncle headers are missing
        """
        # if header.uncles_hash == EMPTY_UNCLE_HASH:
        #     uncles: Tuple[BlockHeaderAPI, ...] = ()
        # else:
        #     try:
        #         uncles = chaindb.get_block_uncles(header.uncles_hash)
        #     except HeaderNotFound as exc:
        #         raise BlockNotFound(f"Uncles not found in database for {header}: {exc}") from exc

        try:
            transactions = chaindb.get_block_transactions(header, cls.get_transaction_builder())
        except MissingTrieNode as exc:
            raise BlockNotFound(f"Transactions not found in database for {header}: {exc}") from exc

        return cls(
            header=header,
            transactions=transactions,
            # uncles=uncles,
        )