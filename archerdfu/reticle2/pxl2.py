"""legacy PXL2 format for accelerometer reticles"""

from construct import Struct, Const, Int32ul, Int32sl, RawCopy, GreedyBytes, Computed, ConstructError
from typing_extensions import Optional, IO

from archerdfu.reticle2 import Reticle2ListContainer, Reticle2, Reticle2Frame, Reticle2DecodeError, Reticle2EncodeError
from archerdfu.reticle2.pxl3 import _PXL3Compressor
from archerdfu.reticle2.typedefs import TReticle2Index, _zoom_slice

PXL2ID = b'PXL2'
PXL2_ZOOM_COUNT = 3

TPXL2Header = Struct(
    PXL2Id=Const(PXL2ID),
    ReticleCount=Int32sl,
    SizeOfAllDataPXL2=Int32ul,
)

TPXL2HeaderSize = TPXL2Header.sizeof()


def _reticles_slice(ctx):
    reticle = []
    for i in range(len(ctx._root.index)):
        buf = _zoom_slice(ctx, ctx._root.index[i])
        reticle.append(buf)
    return reticle


TPXL2Reticle = Struct(
    'header' / TPXL2Header,
    'index' / TReticle2Index[PXL2_ZOOM_COUNT][lambda ctx: ctx._root.header.ReticleCount],
    'data' / RawCopy(GreedyBytes),
    'reticles' / Computed(_reticles_slice),
)


class _PXL2Compressor(_PXL3Compressor):

    def compress(self, __list: Optional[Reticle2ListContainer]):
        self.__init__()
        index_len = len(__list) * PXL2_ZOOM_COUNT
        index_size = index_len * TReticle2Index.sizeof()
        self.offset = TPXL2HeaderSize + index_size
        data_size = self._compress_reticle_list(__list, len(__list), PXL2_ZOOM_COUNT)
        indexes = [self.indexes[i:i + PXL2_ZOOM_COUNT] for i in range(0, index_len, PXL2_ZOOM_COUNT)]
        buffer = TPXL2Reticle.build({
            'header': {
                'ReticleCount': len(__list),
                'SizeOfAllDataPXL2': TPXL2HeaderSize + index_size + data_size,
            },
            'index': indexes,
            'data': {'value': self.buffer},
        })

        return buffer

    @staticmethod
    def decompress(__b: bytes) -> Reticle2ListContainer:
        container = TPXL2Reticle.parse(__b)
        index, rle = None, None

        reticles_list = Reticle2ListContainer()
        for i, subcon in enumerate(container.index):
            reticle = Reticle2()
            for z, zoom in enumerate(subcon):
                _index = zoom
                if _index != index:
                    _rle = container.reticles[i][z]
                    if _rle != rle:
                        reticle[z] = Reticle2Frame(_rle)
                        rle = _rle
                    index = _index
            reticles_list.append(reticle)
        return reticles_list


def loads(__b: bytes) -> Reticle2ListContainer:
    try:
        return _PXL2Compressor.decompress(__b)
    except (ValueError, TypeError) as e:
        raise Reticle2DecodeError(str(e))
    except ConstructError as err:
        raise Reticle2DecodeError("File parsing error", path=err.path)


def load(__fp: IO[bytes]):
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.pxl2', 'rb')`") from None
    b = __fp.read()
    return loads(b)


def dumps(__o: Reticle2ListContainer) -> bytes:
    try:
        try:
            return _PXL2Compressor().compress(__o)
        except ConstructError as err:
            raise Reticle2EncodeError("File building error", err.path)
    except (ValueError, TypeError) as e:
        raise Reticle2EncodeError(str(e))


def dump(__o: Reticle2ListContainer, __fp: IO[bytes]) -> None:
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.pxl2', 'wb')`") from None
    b = dumps(__o)
    __fp.write(b)
