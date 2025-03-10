from typing import Type

from construct import ConstructError
from typing_extensions import IO

from archerdfu.reticle2.reticle2 import Reticle2Container, Reticle2ListContainer, reticle2img, Reticle2, Reticle2Frame
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
        container = TReticle2Parse.parse(__b)
        reticle = Reticle2Container(
            small=Reticle2ListContainer(
                *(Reticle2(
                    *(Reticle2Frame(frame) for frame in reticle)
                ) for reticle in container.reticles.small)
            ),
            hold=Reticle2ListContainer(
            ),
            base=Reticle2ListContainer(
                *(Reticle2(
                    *(Reticle2Frame(frame) for frame in reticle)
                ) for reticle in container.reticles.base)
            ),
            lrf=Reticle2ListContainer(
                *(Reticle2(
                    *(Reticle2Frame(frame) for frame in reticle)
                ) for reticle in container.reticles.lrf)
            ),
        )
        # print(reticle)
        # return container
        return reticle
    except (ValueError, TypeError) as e:
        raise Reticle2DecodeError(str(e))
    except ConstructError as err:
        raise Reticle2DecodeError("File parsing error", __b, err.path)


def load(__fp: IO[bytes]):
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.reticle2', 'rb')`") from None
    b = __fp.read()
    return loads(b)


if __name__ == '__main__':
    from threading import Thread
    from pathlib import Path


    def extract_reticle2(src, dest, *, extract_hold=False):

        with open(src, 'rb') as fp:
            reticle = load(fp)

        def dump(frame, path):
            frame.save(path)

        Path(dest).mkdir(parents=True, exist_ok=True)

        threads = []

        reticle.pop("_io", None)
        if not extract_hold:
            reticle.pop("hold")

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


    extract_reticle2(f'../../assets/example.pxl8', "../../assets/pxl8")
    extract_reticle2(f'../../assets/example.pxl4', "../../assets/pxl4")
