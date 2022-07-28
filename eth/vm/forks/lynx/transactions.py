from abc import ABC

from eth_keys.datatypes import PrivateKey

from eth._utils.transactions import (
    create_transaction_signature,
)
from eth.vm.forks.gray_glacier.transactions import (
    GrayGlacierLegacyTransaction,
    GrayGlacierTransactionBuilder,
    GrayGlacierUnsignedLegacyTransaction,
)


class LynxLegacyTransaction(GrayGlacierLegacyTransaction, ABC):
    pass


class LynxUnsignedLegacyTransaction(GrayGlacierUnsignedLegacyTransaction):
    def as_signed_transaction(
        self,
        private_key: PrivateKey,
        chain_id: int = None
    ) -> LynxLegacyTransaction:
        v, r, s = create_transaction_signature(self, private_key, chain_id=chain_id)
        return LynxLegacyTransaction(
            nonce=self.nonce,
            gas_price=self.gas_price,
            gas=self.gas,
            to=self.to,
            value=self.value,
            data=self.data,
            v=v,
            r=r,
            s=s,
        )


class LynxTransactionBuilder(GrayGlacierTransactionBuilder):
    legacy_signed = LynxLegacyTransaction
    legacy_unsigned = LynxUnsignedLegacyTransaction