"""legacy PXL3 format for wind reticles"""

from construct import Struct, Const, Default, Int32sl, Int32ul, RawCopy, GreedyBytes, Computed, \
    ConstructError
from typing_extensions import Optional, IO

from archerdfu.reticle2 import Reticle2Frame, Reticle2, Reticle2ListContainer, Reticle2DecodeError, Reticle2EncodeError
from archerdfu.reticle2.typedefs import TReticle2Index, _zoom_slice

PXL3ID = b'PXL3'
PXL3_ZOOM_COUNT = 4
PXL3_RETICLES_COUNT = 32  # NOTE: probably not


def _reticles_slice(ctx):
    reticle = []
    for i in range(len(ctx._root.index)):
        buf = _zoom_slice(ctx, ctx._root.index[i])
        reticle.append(buf)
    return reticle


TPXL3Header = Struct(
    'PXLId' / Const(PXL3ID),
    'ReticleCount' / Default(Int32sl, 0),
    'SizeOfAllDataPXL2' / Default(Int32ul, 0),
)

TPXL3HeaderSize = TPXL3Header.sizeof()

TPXL3Reticle = Struct(
    'header' / TPXL3Header,
    'index' / TReticle2Index[PXL3_ZOOM_COUNT][lambda ctx: ctx._root.header.ReticleCount],
    'data' / RawCopy(GreedyBytes),
    'reticles' / Computed(_reticles_slice),
)


class _PXL3Compressor:
    def __init__(self):
        self.indexes = []
        self.base_offset = 0
        self.offset = 0
        self.last_hash = None
        self.buffer = bytearray()

    def _compress_reticle_list(self, __list: Optional[Reticle2ListContainer], reticle_count, zoom_count) -> int:
        start_buf_len = len(self.buffer)

        if not __list:
            self.indexes.extend([self.indexes[-1]] * reticle_count * zoom_count)
            return 0

        for i in range(reticle_count):
            for z in range(zoom_count):

                try:
                    zoom = __list[i][z]
                    if zoom is None or hash(zoom) == self.last_hash:
                        raise IndexError("Empty or non-unique")
                except IndexError:
                    # writing previous index
                    self.indexes.append(self.indexes[-1])
                else:
                    # writing new zoom data
                    self.buffer += zoom.rle
                    self.indexes.append({'offset': self.offset, 'quant': len(zoom) // 4})
                    self.offset = self.base_offset + len(self.buffer)
                    self.last_hash = hash(zoom)

        return len(self.buffer) - start_buf_len

    def compress(self, __list: Optional[Reticle2ListContainer]):
        self.__init__()
        index_len = len(__list) * PXL3_ZOOM_COUNT
        index_size = index_len * TReticle2Index.sizeof()

        self.offset = TPXL3HeaderSize + index_size
        data_size = self._compress_reticle_list(__list, len(__list), PXL3_ZOOM_COUNT)

        indexes = [self.indexes[i:i + PXL3_ZOOM_COUNT] for i in range(0, index_len, PXL3_ZOOM_COUNT)]
        buffer = TPXL3Reticle.build({
            'header': {
                'ReticleCount': len(__list),
                'SizeOfAllDataPXL2': TPXL3HeaderSize + index_size + data_size,
            },
            'index': indexes,
            'data': {'value': self.buffer},
        })

        return buffer

    @staticmethod
    def decompress(__b: bytes) -> Reticle2ListContainer:
        container = TPXL3Reticle.parse(__b)
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
        return _PXL3Compressor.decompress(__b)
    except (ValueError, TypeError) as e:
        raise Reticle2DecodeError(str(e))
    except ConstructError as err:
        raise Reticle2DecodeError("File parsing error", path=err.path)


def load(__fp: IO[bytes]):
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.pxl3', 'rb')`") from None
    b = __fp.read()
    return loads(b)


def dumps(__o: Reticle2ListContainer) -> bytes:
    try:
        try:
            return _PXL3Compressor().compress(__o)
        except ConstructError as err:
            raise Reticle2EncodeError("File building error", err.path)
    except (ValueError, TypeError) as e:
        raise Reticle2EncodeError(str(e))


def dump(__o: Reticle2ListContainer, __fp: IO[bytes]) -> None:
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.pxl3', 'wb')`") from None
    b = dumps(__o)
    __fp.write(b)
