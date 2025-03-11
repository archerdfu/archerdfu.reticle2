from pathlib import Path

import pytest

from archerdfu.reticle2 import loads, dumps, load, Reticle2Container

ASSETS_DIR = Path(__file__).parent.parent / 'assets'
TEST_FILES = [
    ASSETS_DIR / 'dump.pxl4',
    ASSETS_DIR / 'example.pxl4',
    ASSETS_DIR / 'example.pxl8',
]


@pytest.mark.parametrize("file_path", TEST_FILES)  # Correct usage
def test_load(file_path: str) -> None:
    with open(file_path, "rb") as fp:
        r = load(fp)

    assert isinstance(r, Reticle2Container)  # Add an actual assertion

    with open(file_path, "rb") as fp:
        r = load(fp, load_hold=True)

    assert isinstance(r, Reticle2Container)  # Add an actual assertion


# @pytest.mark.parametrize("file_path", ['../assets/dump3.pxl4'])  # Correct usage
# def test_dumps(file_path: str) -> None:
#
#     with open(file_path, "rb") as fp:
#         in_buf = fp.read()
#         r = loads(in_buf)
#
#     out_buf = dumps(r)
#
#     print(len(in_buf), len(out_buf))
#     assert in_buf != out_buf  # Add an actual assertion

@pytest.mark.parametrize("file_path", [ASSETS_DIR / 'dump3.pxl4'])  # Correct usage
def test_dumps_with_hold(file_path: str) -> None:
    with open(file_path, "rb") as fp:
        in_buf = fp.read()
        r = loads(in_buf, load_hold=True)

    out_buf = dumps(r, dump_hold=True)

    assert in_buf == out_buf  # Add an actual assertion
