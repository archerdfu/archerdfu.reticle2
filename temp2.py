PXL8Header = Struct(
    'PXL2Id' / Const(b'PXL8'),
    'ReticleCount' / Anchor(Def(Int32sl, 0)),
    'SizeOfAllDataPXL2' / Anchor(Def(Int32ul, 0)),

    'SmallCount' / Def(Int32ul, 0),
    'OffsetSmall' / Def(Int32ul, 0),
    'SmallSize' / Def(Int32ul, 0),

    'HoldOffCount' / Def(Int32ul, 0),
    'OffsetHoldOff' / Def(Int32ul, 0),
    'HoldOffSize' / Def(Int32ul, 0),
    'HoldOffCrc' / Anchor(Def(Int32ul, 0)),

    'BaseCount' / Def(Int32ul, 0),
    'OffsetBase' / Def(Int32ul, 0),
    'BaseSize' / Def(Int32ul, 0),

    'LrfCount' / Def(Int32ul, 0),
    'OffsetLrf' / Def(Int32ul, 0),
    'LrfSize' / Def(Int32ul, 0),

    Ptr(
        lambda ctx: ctx.ReticleCount.offset1,
        Reb(
            Int32sl,
            lambda ctx: ctx.SmallCount + ctx.HoldOffCount + ctx.BaseCount + ctx.LrfCount
        )
    ),
    Ptr(
        lambda ctx: ctx.SizeOfAllDataPXL2.offset1,
        Reb(
            Int32sl,
            lambda ctx: ctx.OffsetLrf + ctx.LrfSize
        )
    )
)