from typing import Type
from eth.abc import TransactionExecutorAPI
from .computation import LynxComputation
from eth.vm.forks.gray_glacier.state import GrayGlacierState
from eth.vm.forks.gray_glacier.state import GrayGlacierTransactionExecutor


class LynxTransactionExecutor(GrayGlacierTransactionExecutor):
    pass


class LynxState(GrayGlacierState):
    computation_class = LynxComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = LynxTransactionExecutor