from pathlib import Path

import pytest

from archerdfu.reticle2 import (loads, dumps, load, Reticle2Container, Reticle2ListContainer,
                                mksmall, Reticle2, mkhold, PXL4ID, dump, PXL8ID)


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


@pytest.mark.parametrize("file_path", [ASSETS_DIR / 'example.pxl4'])  # Correct usage
def test_dumps_no_hold_pxl4(file_path: str) -> None:
    with open(file_path, "rb") as fp:
        in_buf = fp.read()
        r = loads(in_buf)

    out_buf = dumps(r)
    print(len(in_buf), len(out_buf))
    assert in_buf != out_buf


@pytest.mark.parametrize("file_path", [ASSETS_DIR / 'example.pxl8'])  # Correct usage
def test_dumps_no_hold_pxl8(file_path: str) -> None:
    with open(file_path, "rb") as fp:
        in_buf = fp.read()
        r = loads(in_buf)

    out_buf = dumps(r, PXL8ID)
    print(len(in_buf), len(out_buf))
    assert in_buf != out_buf


@pytest.mark.parametrize("file_path", [ASSETS_DIR / 'dump2.pxl4'])  # Correct usage
def test_dumps_no_hold_to_hold(file_path: str) -> None:
    with open(file_path, "rb") as fp:
        in_buf = fp.read()
        r = loads(in_buf)

    out_buf = dumps(r, dump_hold=True)
    r2 = loads(out_buf)
    out_buf2 = dumps(r2)

    print(len(in_buf), len(out_buf), len(out_buf2))
    assert in_buf != out_buf
    assert out_buf != out_buf2


@pytest.mark.parametrize("file_path", [ASSETS_DIR / 'dump3.pxl4'])  # Correct usage
def test_dumps_hold_to_hold(file_path: str) -> None:
    with open(file_path, "rb") as fp:
        in_buf = fp.read()
        r = loads(in_buf, load_hold=True)

    out_buf = dumps(r, dump_hold=True)

    assert in_buf == out_buf  # Add an actual assertion


# @pytest
def test_create_hold() -> None:
    rng = tuple(range(100, 1000, 100))
    click = int(1.42 * 1000)
    r = Reticle2Container(
        small=Reticle2ListContainer(
            Reticle2(
                mksmall()
            )
        ),
        hold=Reticle2ListContainer(
            Reticle2(
                mkhold(rng, 100, click, 1),
                mkhold(rng, 100, click, 2),
                mkhold(rng, 100, click, 3),
                mkhold(rng, 100, click, 4),
            )
        ),
    )
    # copy hold to base to view
    r.base = Reticle2ListContainer(
        r.hold[0]
    )
    with open(ASSETS_DIR / "gen_hold.pxl4", "wb") as fp:
        dump(r, fp, PXL4ID, dump_hold=True)
