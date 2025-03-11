from construct import (Struct, RawCopy, Default, Int32sl, Const, Int32ul, Select, Switch,
                       ByteSwapped, BitStruct, BitsInteger, Computed, GreedyBytes)
from typing_extensions import Literal

PXL4ID = b'PXL4'
PXL8ID = b'PXL8'

PXL4COUNT = 4
PXL8COUNT = 8

SMALL_RETICLES_COUNT = 20
HOLD_RETICLES_COUNT = 20

Reticle2Type = Literal[b'PXL4', b'PXL8']

TReticle2FileHeader = Struct(
    'PXLId' / Select(Const(PXL4ID), Const(PXL8ID)),
    'ReticleCount' / Default(Int32sl, 0),
    'SizeOfAllDataPXL2' / Default(Int32ul, 0),

    'SmallCount' / Default(Int32ul, SMALL_RETICLES_COUNT),
    'OffsetSmall' / Default(Int32ul, 0),
    'SmallSize' / Default(Int32ul, 0),

    'HoldOffCount' / Default(Int32ul, HOLD_RETICLES_COUNT),
    'OffsetHoldOff' / Default(Int32ul, 0),
    'HoldOffSize' / Default(Int32ul, 0),
    'HoldOffCrc' / Default(Int32sl, 0),

    'BaseCount' / Default(Int32ul, 0),
    'OffsetBase' / Default(Int32ul, 0),
    'BaseSize' / Default(Int32ul, 0),

    'LrfCount' / Default(Int32ul, 0),
    'OffsetLrf' / Default(Int32ul, 0),
    'LrfSize' / Default(Int32ul, 0),
)

TReticle2FileHeaderSize = Int32sl[16].sizeof()

TReticle2Index = Struct(
    'offset' / Default(Int32ul, 0),
    'quant' / Default(Int32ul, 0)
)

TReticle2IndexSize = Int32sl[2].sizeof()

TReticle2IndexArray = Switch(
    lambda ctx: ctx._root.header.PXLId,
    {
        PXL4ID: TReticle2Index[PXL4COUNT],
        PXL8ID: TReticle2Index[PXL8COUNT],
    }
)

TReticle2Data = ByteSwapped(BitStruct(
    'x' / BitsInteger(12),
    'y' / BitsInteger(10),
    'q' / BitsInteger(10),
))

TReticle2DataSize = TReticle2Data.sizeof()


def _zoom_slice(ctx, index):
    zooms = []
    for i, zoom in enumerate(index):
        start = (zoom.offset - ctx._root.data.offset1)
        end = start + (zoom.quant * TReticle2DataSize)
        zooms.append(ctx._root.data.value[start:end])
    return zooms


def _reticles_slice(ctx):
    computed = {}
    for key in ('small', 'hold', 'base', 'lrf'):
        zooms = []
        for i in range(len(ctx._root.index[key])):
            buf = _zoom_slice(ctx, ctx._root.index[key][i])
            zooms.append(buf)
        computed[key] = zooms
    return computed


TReticle2IndexHeader = Struct(
    'small' / TReticle2IndexArray[lambda ctx: ctx._root.header.SmallCount],
    'hold' / TReticle2IndexArray[lambda ctx: ctx._root.header.HoldOffCount],
    'base' / TReticle2IndexArray[lambda ctx: ctx._root.header.BaseCount],
    'lrf' / TReticle2IndexArray[lambda ctx: ctx._root.header.LrfCount],
)

TReticle2Parse = Struct(
    'header' / TReticle2FileHeader,
    'index' / TReticle2IndexHeader,
    'data' / RawCopy(GreedyBytes),
    'reticles' / Computed(_reticles_slice),
)

TReticle2Build = Struct(
    'header' / TReticle2FileHeader,
    'index' / Switch(
        lambda ctx: ctx._root.header.PXLId,
        {
            PXL4ID: TReticle2Index[lambda ctx: ctx._root.header.ReticleCount * PXL4COUNT],
            PXL8ID: TReticle2Index[lambda ctx: ctx._root.header.ReticleCount * PXL8COUNT]
        }
    ),
    'data' / GreedyBytes
)
