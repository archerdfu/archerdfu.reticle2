from construct import Struct, RawCopy, Default, Int32sl, Const, Int32ul, Pointer, Rebuild, Index, Select, Switch, Array, \
    GreedyRange, Tell, ByteSwapped, BitStruct, BitsInteger, ListContainer, Computed

# PXL2ID = b'PXL2'
PXL4ID = b'PXL4'
PXL8ID = b'PXL8'

PXL4COUNT = 4
PXL8COUNT = 8

# PXL2Header = Struct(
#     PXL2Id=Const(PXL2ID),
#     number_of_reticle=Int32ul,
#     size_of_all_data_PXL2=Int32ul,
# )

TReticle2Header = Struct(
    'PXLId' / Select(Const(PXL4ID), Const(PXL8ID)),
    'ReticleCount' / RawCopy(Default(Int32sl, 0)),
    'SizeOfAllDataPXL2' / RawCopy(Default(Int32ul, 0)),

    'SmallCount' / Default(Int32ul, 0),
    'OffsetSmall' / Default(Int32ul, 0),
    'SmallSize' / Default(Int32ul, 0),

    'HoldOffCount' / Default(Int32ul, 0),
    'OffsetHoldOff' / Default(Int32ul, 0),
    'HoldOffSize' / Default(Int32ul, 0),
    'HoldOffCrc' / RawCopy(Default(Int32ul, 0)),

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

TReticle2Index = Struct(
    'idx' / Index,
    'offset' / Default(Int32ul, 0),
    'quant' / Default(Int32ul, 0)
)

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

def compute_ret_data(ctx, index):
    zooms = ListContainer()

    for i, zoom in enumerate(index):
        if i == 0 or (i > 0 and index[i].offset != index[i - 1].offset) and zoom.quant > 0:
            start = (zoom.offset - ctx._root.offset) // TReticle2Data.sizeof()
            end = start + zoom.quant
            zooms.append(ctx._root.data[start:end])
        else:
            zooms.append([])
    return zooms

TReticleComputed = Struct(
    'small' / Array(
        lambda ctx: len(ctx._root.index.small),
        Computed(lambda ctx: compute_ret_data(ctx, ctx._root.index.small[ctx._index]))
    ),
    'hold' / Array(
        lambda ctx: len(ctx._root.index.hold),
        Computed(lambda ctx: compute_ret_data(ctx, ctx._root.index.hold[ctx._index]))
    ),
    'base' / Array(
        lambda ctx: len(ctx._root.index.base),
        Computed(lambda ctx: compute_ret_data(ctx, ctx._root.index.base[ctx._index]))
    ),
    'lrf' / Array(
        lambda ctx: len(ctx._root.index.lrf),
        Computed(lambda ctx: compute_ret_data(ctx, ctx._root.index.lrf[ctx._index]))
    )
)

TReticle2Parse = Struct(

    'header' / TReticle2Header,
    'index' / Struct(
        'small' / Array(lambda ctx: ctx._root.header.SmallCount, TReticle2IndexArray),
        'hold' / Array(lambda ctx: ctx._root.header.HoldOffCount, TReticle2IndexArray),
        'base' / Array(lambda ctx: ctx._root.header.BaseCount, TReticle2IndexArray),
        'lrf' / Array(lambda ctx: ctx._root.header.LrfCount, TReticle2IndexArray),
    ),
    'offset' / Tell,
    'data' / GreedyRange(TReticle2Data),
    'reticles' / TReticleComputed,
)

TReticle2Build = Struct(
    'header' / TReticle2Header,
    'index' / Switch(
        lambda ctx: ctx._root.header.PXLId,
        {
            PXL4ID: TReticle2Index[lambda ctx: (ctx.SmallCount + ctx.HoldOffCount + ctx.BaseCount + ctx.LrfCount) * PXL4COUNT],
            PXL8ID: TReticle2Index[lambda ctx: (ctx.SmallCount + ctx.HoldOffCount + ctx.BaseCount + ctx.LrfCount) * PXL8COUNT]
        }
    ),
    'data' / GreedyRange(TReticle2Data)
)
