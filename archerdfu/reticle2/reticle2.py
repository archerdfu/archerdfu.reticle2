from construct import ConstructError
from typing_extensions import IO

from archerdfu.reticle2 import framebuf
from archerdfu.reticle2.bmp import _create_bmp_headers, BMP
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

    # Build bmp from framebuffer
    header_data, dib_header_data = _create_bmp_headers((width, height), 24)
    # Convert the matrix of pixels to bytes
    pixel_data = (f_buf.pixel(x, y).to_bytes(3, 'big') for y in reversed(range(height)) for x in range(width))

    # Create the BMP data
    bmp_data = {
        "header": header_data,
        "dib_header": dib_header_data,
        "color_palette": None,
        "pixel_data": pixel_data,
    }
    return BMP.build(bmp_data)


if __name__ == '__main__':
    from threading import Thread
    from pathlib import Path
    # from PIL import Image
    # from io import BytesIO

    def extract_reticle2(src, dest, *, extract_hold=False):

        with open(src, 'rb') as fp:
            reticle = load(fp)

        def dump(con, path):
            buf = reticle2bmp(con)
            # img = Image.open(BytesIO(buf))
            # img.show()
            # exit(1)
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
                    break
        for t in threads:
            t.start()

        for t in threads:
            t.join()


    extract_reticle2(f'../../assets/example.pxl8', "../../assets/pxl8")
    extract_reticle2(f'../../assets/example.pxl4', "../../assets/pxl4")
