from email.header import Header
from typing import (
    Type,
)
from eth.rlp.blocks import BaseBlock
from eth.vm.state import BaseState
from .headers import (create_header_from_parent, configure_header)
from .state import LynxState
from .blocks import LynxBlock
from eth.vm.forks.gray_glacier import GrayGlacierVM
from eth.abc import (
    BlockHeaderAPI,
)
from eth_utils import (
    ValidationError,
)
from eth.validation import (
    validate_length_lte,
)

class LynxVM(GrayGlacierVM):
    # Fork Name
    fork = 'lynx'

    # Classes
    block_class: Type[BaseBlock] = LynxBlock
    _state_class: Type[BaseState] = LynxState

    # Methods
    create_header_from_parent = create_header_from_parent

    # configure_header = configure_header

    @classmethod
    def validate_header(cls,
                        header: BlockHeaderAPI,
                        parent_header: BlockHeaderAPI) -> None:

        if parent_header is None:
            # to validate genesis header, check if it equals canonical header at block number 0
            raise ValidationError("Must have access to parent header to validate current header")
        else:
            validate_length_lte(
                header.extra_data, cls.extra_data_max_bytes, title="BlockHeader.extra_data")

            # cls.validate_gas(header, parent_header)

            if header.block_number != parent_header.block_number + 1:
                raise ValidationError(
                    "Blocks must be numbered consecutively. "
                    f"Block number #{header.block_number} "
                    f"has parent #{parent_header.block_number}"
                )

            # timestamp
            if header.timestamp <= parent_header.timestamp:
                raise ValidationError(
                    "timestamp must be strictly later than parent, "
                    f"but is {parent_header.timestamp - header.timestamp} seconds before.\n"
                    f"- child  : {header.timestamp}\n"
                    f"- parent : {parent_header.timestamp}. "
                )


    