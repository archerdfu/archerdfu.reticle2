from construct import ConstructError
from typing_extensions import IO, Any

from archerdfu.reticle2.reticle2 import Reticle2Container


class DEPRECATED_DEFAULT:
    """Sentinel to be used as default arg during deprecation
    period of Reticle2DecodeError free-form arguments."""


class Reticle2DecodeError(ValueError):

    def __init__(
            self,
            msg: str = DEPRECATED_DEFAULT,
            doc: Any = DEPRECATED_DEFAULT,
            path: str = DEPRECATED_DEFAULT,
            *args,
    ):
        if (
                args
                or not isinstance(msg, str)
                or not isinstance(path, str)
        ):
            import warnings

            warnings.warn(
                "Free-form arguments for Reticle2DecodeError are deprecated. "
                "Please set 'msg' (str) and 'path' (str) arguments only.",
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


def loads(__b: bytes, *, load_hold: bool = False):
    try:
        return Reticle2Container.decompress(__b, decompress_hold=load_hold)
    except (ValueError, TypeError) as e:
        raise Reticle2DecodeError(str(e))
    except ConstructError as err:
        raise Reticle2DecodeError("File parsing error", path=err.path)


def load(__fp: IO[bytes], *, load_hold: bool = False):
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.reticle2', 'rb')`") from None
    b = __fp.read()
    return loads(b, load_hold=load_hold)


if __name__ == '__main__':
    from threading import Thread
    from pathlib import Path


    def extract_reticle2(src, dest, *, extract_hold=False):

        with open(src, 'rb') as fp:
            reticle = load(fp, load_hold=extract_hold)

        Path(dest).mkdir(parents=True, exist_ok=True)

        threads = []

        for k, con in reticle.items():

            for i, ret in enumerate(con):

                for j, frame in enumerate(ret):

                    if frame is not None:
                        if len(frame) <= 0 or (j != 0 and ret[0] == frame):
                            continue

                        filename = Path(dest, f"{k}_{str(i + 1)}_{j + 1}.bmp")
                        threads.append(Thread(target=frame.save, args=[filename]))

        for t in threads:
            t.start()

        for t in threads:
            t.join()


    # extract_reticle2(f'../../assets/example.pxl8', "../../assets/pxl8")
    # extract_reticle2(f'../../assets/example.pxl4', "../../assets/pxl4")
    extract_reticle2(f'../../assets/dump.pxl4', "../../assets/dump", extract_hold=True)
