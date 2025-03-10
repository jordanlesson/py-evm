from typing import (
    Iterable,
    Optional,
)

from eth_typing import (
    Address,
    BlockNumber,
    Hash32,
)

from eth.abc import ExecutionContextAPI
from eth._utils.generator import CachedIterable


class ExecutionContext(ExecutionContextAPI):
    _coinbase = None
    _timestamp = None
    _number = None
    _difficulty = None
    _gas_limit = None
    _prev_hashes = None
    _chain_id = None
    _base_fee_per_gas = None
    # _epoch = None
    # _slot = None

    def __init__(
            self,
            coinbase: Address,
            timestamp: int,
            block_number: BlockNumber,
            prev_hashes: Iterable[Hash32],
            chain_id: int,
            # epoch: int,
            # slot: int,
            difficulty: int = 0,
            gas_limit: int = 0,
            base_fee_per_gas: Optional[int] = 0,
            ) -> None:
        self._coinbase = coinbase
        self._timestamp = timestamp
        self._block_number = block_number
        self._difficulty = difficulty
        self._gas_limit = gas_limit
        self._prev_hashes = CachedIterable(prev_hashes)
        self._chain_id = chain_id
        self._base_fee_per_gas = base_fee_per_gas
        # self._epoch = epoch
        # self._slot = slot

    @property
    def coinbase(self) -> Address:
        return self._coinbase

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def block_number(self) -> BlockNumber:
        return self._block_number

    @property
    def difficulty(self) -> int:
        if self._difficulty > 0:
            return 0
        else:
            return self._difficulty

    @property
    def gas_limit(self) -> int:
        return self._gas_limit

    @property
    def prev_hashes(self) -> Iterable[Hash32]:
        return self._prev_hashes

    @property
    def chain_id(self) -> int:
        return self._chain_id

    @property
    def base_fee_per_gas(self) -> int:
        if self._base_fee_per_gas is None:
            raise AttributeError(
                f"This header at Block #{self.block_number} does not have a base gas fee"
            )
        else:
            return self._base_fee_per_gas

    # @property
    # def epoch(self) -> int:
    #     return self._epoch

    # @property
    # def slot(self) -> int:
    #     return self._slot
