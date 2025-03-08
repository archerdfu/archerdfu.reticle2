from construct import ConstructError
from typing_extensions import IO

from archerdfu.reticle2 import framebuf
from archerdfu.reticle2.bmp import matrix_to_bmp
from archerdfu.reticle2.typedefs import TReticle2Parse


class DEPRECATED_DEFAULT:
    """Sentinel to be used as default arg during deprecation
    period of Reticle2DecodeError free-form arguments."""


class Reticle2DecodeError(ValueError):

    def __init__(
            self,
            msg: str = DEPRECATED_DEFAULT,
            doc: bytes = DEPRECATED_DEFAULT,
            path: str = DEPRECATED_DEFAULT,
            *args,
    ):
        if (
                args
                or not isinstance(msg, str)
                or not isinstance(doc, bytes)
                or not isinstance(path, str)
        ):
            import warnings

            warnings.warn(
                "Free-form arguments for Reticle2DecodeError are deprecated. "
                "Please set 'msg' (str), 'doc' (bytes) and 'path' (str) arguments only.",
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


def loads(__b: bytes):
    try:
        return TReticle2Parse.parse(__b)
    except ConstructError as err:
        raise Reticle2DecodeError("File parsing error", __b, err.path)


def load(__fp: IO[bytes]):
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.reticle2', 'rb')`") from None
    b = __fp.read()
    return loads(b)


def reticle2bmp(img_data, size=(640, 480), cross=False, grid=False):
    width, height = size
    buf = bytearray(width * height * 3)  # RGB888 buffer
    f_buf = framebuf.FrameBuffer(buf, width, height, framebuf.RGB888)
    f_buf.fill(0xFFFFFF)  # White background

    # Draw crosshair
    if cross:
        mid_x, mid_y = width // 2, height // 2
        f_buf.line(0, mid_y, width - 1, mid_y, 0x0000FF)  # Horizontal
        f_buf.line(mid_x, 0, mid_x, height - 1, 0x0000FF)  # Vertical

    # Draw elements
    for el in img_data:
        if grid and el.x == 700 and el.q == 0:
            f_buf.line(340, 240 + el.y, 640, 240 + el.y, 0x00CF00)

        f_buf.line(el.x, el.y, el.x + el.q - 1, el.y, 0x000000)

    # Convert framebuffer buffer to BMP pixel matrix
    matrix = []
    row_size = width * 3  # 3 bytes per pixel (RGB888)
    for y in reversed(range(height)):  # BMP stores pixels bottom-up
        row_start = y * row_size
        row = []
        for x in range(0, row_size, 3):
            b, g, r = buf[row_start + x:row_start + x + 3]  # Extract RGB components
            row.append((r << 16) | (g << 8) | b)  # Convert to 0xRRGGBB format
        matrix.append(row)

    return matrix_to_bmp(matrix)


def extract_reticle2(src, dest, *, extract_hold=False):
    from threading import Thread
    from pathlib import Path

    with open(src, 'rb') as fp:
        reticle = load(fp)

    def dump(con, path):
        buf = reticle2bmp(con)

        with open(path, 'wb') as fp:
            fp.write(buf)

    Path(dest).mkdir(parents=True, exist_ok=True)

    threads = []

    reticle.reticles.pop("_io")
    if not extract_hold:
        reticle.reticles.pop("hold")

    for k, v in reticle.reticles.items():

        for i, ret in enumerate(v):

            for j, z in enumerate(ret):

                if len(z) <= 0 or (j != 0 and ret[0] == z):
                    continue

                filename = Path(dest, f"{k}_{str(i + 1)}_{j + 1}.bmp")
                threads.append(Thread(target=dump, args=[z.copy(), filename]))

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    extract_reticle2(f'../../assets/example.pxl8', "../../assets/pxl8")
    extract_reticle2(f'../../assets/example.pxl4', "../../assets/pxl4")
