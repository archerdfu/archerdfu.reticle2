from archerdfu.reticle2.reticle2 import Reticle2Frame, rle
from archerdfu.reticle2._hold_off import SMALL_RET, create_hold_reticle

__all__ = ('mksmall', 'mkhold')


def _el2frame(els) -> Reticle2Frame:
    buf = b''.join(rle.pack_record(*i) for i in els)
    return Reticle2Frame(buf)


def mksmall() -> Reticle2Frame:
    return _el2frame(SMALL_RET)


def mkhold(distances: tuple[int, ...] | list[int], zero: int, click_micron: int, zoom=1, *, subsonic=False):
    els = create_hold_reticle(distances, zero, click_micron, zoom, subsonic=subsonic)
    return _el2frame(els)
