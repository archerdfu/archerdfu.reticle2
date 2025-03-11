from construct import ConstructError
from typing_extensions import IO, Any

from archerdfu.reticle2.decode import DEPRECATED_DEFAULT
from archerdfu.reticle2.reticle2 import Reticle2Container
from archerdfu.reticle2.typedefs import Reticle2Type, PXL4ID, PXL8ID


class Reticle2EncodeError(ValueError):

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
                "Free-form arguments for Reticle2EncodeError are deprecated. "
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


def dumps(__o: Reticle2Container, __type: Reticle2Type = PXL4ID, *, dump_hold: bool = False) -> bytes:
    try:
        try:
            return __o.compress(__type, compress_hold=dump_hold)
        except ConstructError as err:
            raise Reticle2EncodeError("File building error", err.path)
    except (ValueError, TypeError) as e:
        raise Reticle2EncodeError(str(e))


def dump(__o: Reticle2Container, __fp: IO[bytes], __type: Reticle2Type = PXL4ID, *, dump_hold: bool = False) -> None:
    if 'b' not in getattr(__fp, 'mode', ''):
        raise TypeError("File must be opened in binary mode, e.g. use `open('foo.reticle2', 'wb')`") from None
    b = dumps(__o, __type, dump_hold=dump_hold)
    __fp.write(b)


if __name__ == '__main__':
    from archerdfu.reticle2.decode import load

    with open(f'../../assets/dump.pxl4', 'rb') as fp:
        con = load(fp, load_hold=True)

    with open("../../assets/dump3.pxl4", 'wb') as fp:
        dump(con, fp, PXL4ID, dump_hold=True)

    with open("../../assets/dump3.pxl8", 'wb') as fp:
        dump(con, fp, PXL8ID, dump_hold=True)
