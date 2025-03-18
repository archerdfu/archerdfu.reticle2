from pathlib import Path

from archerdfu.reticle2.pxl2 import loads, dumps

ASSETS_DIR = Path(__file__).parent.parent / 'assets'
IN_PATH = ASSETS_DIR / 'smallret.pxl2'
OUT_PATH = ASSETS_DIR / 'pxl2'


def test_loads():
    with open(IN_PATH, 'rb') as f1:
        d = f1.read()
    container = loads(d)
    assert len(container) == 1

    import os
    os.makedirs(OUT_PATH, exist_ok=True)
    i = 0
    for r, reticle in enumerate(container):
        for z, zoom in enumerate(reticle):
            if zoom:
                zoom.img.save(OUT_PATH / f'{i}_{z + 1}.bmp')
                i += 1


def test_dumps():
    with open(IN_PATH, 'rb') as f1:
        in_buf = f1.read()
        d = loads(in_buf)

    out_buf = dumps(d)
    assert in_buf[:12] == out_buf[:12]
    assert in_buf[1036:] == out_buf[1036:]
    for i in range(32):
        assert in_buf[12 + i * 8:12 + (i + 1) * 8] == out_buf[12 + i * 8:12 + (i + 1) * 8]

# def test_loads():
#     with open(IN_PATH, 'rb') as f1:
#         container = load(f1)
#
#         import os
#         os.makedirs(OUT_PATH, exist_ok=True)
#         i = 0
#         for r, reticle in enumerate(container):
#             for z, zoom in enumerate(reticle):
#                 if zoom:
#                     zoom.img.save(OUT_PATH / f'{i}_{z + 1}.bmp')
#                     i += 1
#
#
# def test_dumps():
#     with open(IN_PATH, 'rb') as f1:
#         in_buf = f1.read()
#         container = _PXL2Compressor.decompress(in_buf)
#
#     out_buf = _PXL2Compressor().compress(container)
#     assert in_buf[:12] == out_buf[:12]
#     # assert in_buf[1036:] == out_buf[1036:]
#     # for i in range(32):
#     #     assert in_buf[12 + i * 8:12 + (i + 1) * 8] == out_buf[12 + i * 8:12 + (i + 1) * 8]
