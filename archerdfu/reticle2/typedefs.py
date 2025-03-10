from construct import Struct, RawCopy, Default, Int32sl, Const, Int32ul, Pointer, Rebuild, Index, Select, Switch, Array, \
    GreedyRange, ByteSwapped, BitStruct, BitsInteger, ListContainer, Computed, GreedyBytes
from typing_extensions import Literal

# PXL2ID = b'PXL2'
PXL4ID = b'PXL4'
PXL8ID = b'PXL8'

PXL4COUNT = 4
PXL8COUNT = 8

Reticle2Type = Literal[b'PXL4', b'PXL8']

# PXL2Header = Struct(
#     PXL2Id=Const(PXL2ID),
#     number_of_reticle=Int32ul,
#     size_of_all_data_PXL2=Int32ul,
# )


TReticle2FileHeader = Struct(
    'PXLId' / Select(Const(PXL4ID), Const(PXL8ID)),
    'ReticleCount' / RawCopy(Default(Int32sl, 0)),
    'SizeOfAllDataPXL2' / RawCopy(Default(Int32ul, 0)),

    'SmallCount' / Default(Int32ul, 0),
    'OffsetSmall' / Default(Int32ul, 0),
    'SmallSize' / Default(Int32ul, 0),

    'HoldOffCount' / Default(Int32ul, 0),
    'OffsetHoldOff' / Default(Int32ul, 0),
    'HoldOffSize' / Default(Int32ul, 0),
    # 'HoldOffCrc' / RawCopy(Default(Int32ul, 0)),
    'HoldOffCrc' / Default(Int32sl, 0),

    'BaseCount' / Default(Int32ul, 0),
    'OffsetBase' / Default(Int32ul, 0),
    'BaseSize' / Default(Int32ul, 0),

    'LrfCount' / Default(Int32ul, 0),
    'OffsetLrf' / Default(Int32ul, 0),
    'LrfSize' / Default(Int32ul, 0),

    Pointer(
        lambda ctx: ctx.ReticleCount.offset1,
        Rebuild(
            Int32sl,
            lambda ctx: ctx.SmallCount + ctx.HoldOffCount + ctx.BaseCount + ctx.LrfCount
        )
    ),
    Pointer(
        lambda ctx: ctx.SizeOfAllDataPXL2.offset1,
        Rebuild(
            Int32sl,
            lambda ctx: ctx.OffsetLrf + ctx.LrfSize
        )
    ),
)

TReticle2FileHeaderSize = Int32sl[16].sizeof()

TReticle2Index = Struct(
    'idx' / Index,
    'offset' / Default(Int32ul, 0),
    'quant' / Default(Int32ul, 0)
)

TReticle2IndexSize = Int32sl[2].sizeof()

TReticle2IndexArray = Switch(
    lambda ctx: ctx._root.header.PXLId,
    {
        PXL4ID: Array(PXL4COUNT, TReticle2Index),
        PXL8ID: Array(PXL8COUNT, TReticle2Index),
    }
)

TReticle2Data = ByteSwapped(BitStruct(
    'x' / BitsInteger(12),
    'y' / BitsInteger(10),
    'q' / BitsInteger(10),
))

TReticle2DataSize = TReticle2Data.sizeof()


def data_slice(ctx, index):
    zooms = ListContainer()
    for i, zoom in enumerate(index):
        start = (zoom.offset - ctx._root.data.offset1)
        end = start + (zoom.quant * TReticle2DataSize)
        zooms.append(ctx._root.data.value[start:end])
    return zooms


TReticleComputed = Struct(
    'small' / Array(
        lambda ctx: len(ctx._root.index.small),
        Computed(lambda ctx: data_slice(ctx, ctx._root.index.small[ctx._index]))
    ),
    'hold' / Array(
        lambda ctx: len(ctx._root.index.hold),
        Computed(lambda ctx: data_slice(ctx, ctx._root.index.hold[ctx._index]))
    ),
    'base' / Array(
        lambda ctx: len(ctx._root.index.base),
        Computed(lambda ctx: data_slice(ctx, ctx._root.index.base[ctx._index]))
    ),
    'lrf' / Array(
        lambda ctx: len(ctx._root.index.lrf),
        Computed(lambda ctx: data_slice(ctx, ctx._root.index.lrf[ctx._index]))
    )
)

TReticle2IndexHeader = Struct(
    'small' / Array(lambda ctx: ctx._root.header.SmallCount, TReticle2IndexArray),
    'hold' / Array(lambda ctx: ctx._root.header.HoldOffCount, TReticle2IndexArray),
    'base' / Array(lambda ctx: ctx._root.header.BaseCount, TReticle2IndexArray),
    'lrf' / Array(lambda ctx: ctx._root.header.LrfCount, TReticle2IndexArray),
)

TReticle2Parse = Struct(
    'header' / TReticle2FileHeader,
    'index' / TReticle2IndexHeader,
    'data' / RawCopy(GreedyBytes),
    'reticles' / TReticleComputed,
)

TReticle2Build = Struct(
    'header' / TReticle2FileHeader,
    'index' / Switch(
        lambda ctx: ctx._root.header.PXLId,
        {
            PXL4ID: TReticle2Index[
                lambda ctx: (ctx.SmallCount + ctx.HoldOffCount + ctx.BaseCount + ctx.LrfCount) * PXL4COUNT],
            PXL8ID: TReticle2Index[
                lambda ctx: (ctx.SmallCount + ctx.HoldOffCount + ctx.BaseCount + ctx.LrfCount) * PXL8COUNT]
        }
    ),
    'data' / GreedyRange(TReticle2Data)
)
