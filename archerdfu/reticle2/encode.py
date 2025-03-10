from copy import deepcopy

from construct import ConstructError
from typing_extensions import IO, Any

from archerdfu.reticle2.decode import DEPRECATED_DEFAULT
from archerdfu.reticle2.reticle2 import Reticle2Container
from archerdfu.reticle2.typedefs import TReticle2Build, Reticle2Type, PXL4ID, TReticle2FileHeaderSize, PXL8COUNT, \
    TReticle2IndexSize, PXL8ID


class Reticle2EncodeError(ValueError):

    def __init__(
            self,
            msg: str = DEPRECATED_DEFAULT,
            doc: Any = DEPRECATED_DEFAULT,
            path: str = DEPRECATED_DEFAULT,
            *args,
    ):
        if (
                args
                or not isinstance(msg, str)
                or not isinstance(path, str)
        ):
            import warnings

            warnings.warn(
                "Free-form arguments for Reticle2EncodeError are deprecated. "
                "Please set 'msg' (str) and 'path' (str) arguments only.",
                DeprecationWarning,
                stacklevel=2,
            )

            if path is not DEPRECATED_DEFAULT:  # type: ignore[comparison-overlap]
                args = path, *args
            if doc is not DEPRECATED_DEFAULT:  # type: ignore[comparison-overlap]
                args = doc, *args
            if msg is not DEPRECATED_DEFAULT:  # type: ignore[comparison-overlap]
                args = msg, *args
            ValueError.__init__(self, *args)
            return


def dumps(__o: Reticle2Container, __type: Reticle2Type = PXL4ID) -> bytes:
    # try:

        header_size = TReticle2FileHeaderSize
        index_size = con.count * PXL8COUNT * TReticle2IndexSize
        data_size = con.size(__type)

        small_offset = header_size + index_size
        hold_offset = small_offset + con.small.size(__type)
        base_offset = hold_offset + con.hold.size(__type)
        lrf_offset = base_offset + con.base.size(__type)

        prepared = {
            'header': {
                'PXLId': __type,
                'ReticleCount': __o.count,
                'SizeOfAllDataPXL2': header_size + index_size + data_size,

                'SmallCount': len(con.small),
                'OffsetSmall': small_offset,
                'SmallSize': con.small.size(__type),

                'HoldOffCount': len(con.hold),
                'OffsetHoldOff': hold_offset,
                'HoldOffSize': con.hold.size(__type),
                'HoldOffCrc': 0,

                'BaseCount': len(con.base),
                'OffsetBase': base_offset,
                'BaseSize': con.base.size(__type),

                'LrfCount': len(con.lrf),
                'OffsetLrf': lrf_offset,
                'LrfSize': con.lrf.size(__type),
            }
        }
        from pprint import pprint
        pprint(prepared, sort_dicts=False)
        try:
            return TReticle2Build.dumps(prepared)
        except ConstructError as err:
            raise Reticle2EncodeError("File parsing error", prepared, err.path)

    # except (ValueError, TypeError) as e:
    #     raise Reticle2EncodeError(str(e))


def dump(__o: Reticle2Container, __fp: IO[bytes]) -> None:
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.reticle2', 'wb')`") from None
    b = dumps(__o)
    __fp.write(b)


if __name__ == '__main__':
    from archerdfu.reticle2.decode import loads
    # c = Reticle2Container()
    # print(dumps(c))
    with open(f'../../assets/example.pxl8', 'rb') as fp:
        buf = fp.read()
        # container = TReticle2Parse.parse(buf)
        # print(container.header)
        con = loads(buf)

        print(dumps(con, PXL8ID))

        # Container:
        #     PXLId = b'PXL8' (total 4)
        #     ReticleCount = 9
        #     SizeOfAllDataPXL2 = 42704
        #     SmallCount = 1
        #     OffsetSmall = 640
        #     SmallSize = 84
        #     HoldOffCount = 0
        #     OffsetHoldOff = 724
        #     HoldOffSize = 0
        #     HoldOffCrc = 0
        #     BaseCount = 5
        #     OffsetBase = 724
        #     BaseSize = 40904
        #     LrfCount = 3
        #     OffsetLrf = 41628
        #     LrfSize = 1076
