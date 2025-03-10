from dataclasses import dataclass, field
from os import PathLike

from PIL import Image
from typing_extensions import Union, IO, Any, Optional, Literal

from archerdfu.reticle2 import rle
from archerdfu.reticle2.containers import FixedSizeList, RestrictedDict
from archerdfu.reticle2.typedefs import Reticle2Type, PXL4ID, PXL8ID, PXL4COUNT, PXL8COUNT


def reticle2img(buffer: bytes, size=(640, 480)) -> Image.Image:
    return rle.decode(buffer, size)


def img2reticle(img: Image.Image) -> bytes:
    return rle.encode(img)


@dataclass(unsafe_hash=True)
class Reticle2Frame:
    _rle: bytes = field(init=False, default=b'', compare=True, repr=False)
    _img: Optional[Image.Image] = field(init=False, default=None, compare=False)

    def __init__(self, __o: Union[bytes, Image.Image, None] = None):
        if __o is not None:
            if isinstance(__o, bytes):
                self.rle = __o
            elif isinstance(__o, Image.Image):
                self.img = __o
            else:
                raise TypeError('__o must be bytes or Image.Image')

    def __len__(self) -> int:
        return len(self._rle)

    @property
    def rle(self) -> bytes:
        return self._rle

    @property
    def img(self) -> Image.Image:
        return self.img

    @rle.setter
    def rle(self, buffer: bytes):
        self._rle = buffer
        self._img = reticle2img(buffer)

    @img.setter
    def img(self, img: Image.Image):
        self._img = img
        self._rle = img2reticle(img)

    def save(self, fp: str | bytes | PathLike[str] | PathLike[bytes] | IO[bytes],
             format: str | None = None,
             **params: Any) -> None:
        self._img.save(fp, format, **params)

    def open(self, fp: str | bytes | PathLike[str] | PathLike[bytes] | IO[bytes],
             mode: Literal["r"] = "r",
             formats: list[str] | tuple[str, ...] | None = None) -> None:
        self.img = Image.open(fp, mode, formats)


class Reticle2(FixedSizeList):
    value_type = Optional[Reticle2Frame]

    def __init__(self, *frames):
        if not all(isinstance(f, self.value_type) for f in frames):
            raise TypeError("Value should be a type of Reticle2Frame or None")
        super().__init__(*frames, size=8)

    def __setitem__(self, index, value):
        if not (0 <= index < self._size):
            raise IndexError("Index out of range")
        if not isinstance(value, self.value_type):
            raise TypeError("Value should be a type of Reticle2Frame or None")
        super().__setitem__(index, value)

    def __eq__(self, other):
        if not isinstance(other, Reticle2):
            return False
        return tuple(self) == tuple(other)

    def __hash__(self):
        return hash(tuple(self))  # Convert list to tuple for hashing

    def sizeof(self, __type: Reticle2Type = PXL4ID) -> int:
        if __type == PXL8ID:
            unique = set(self[:PXL8COUNT])
        elif __type == PXL4ID:
            unique = set(self[:PXL4COUNT])
        else:
            raise TypeError("Unsupported reticle2 type {!r}".format(__type))
        return sum(len(i) for i in unique if i is not None)

class Reticle2ListContainer(list):
    value_type = Optional[Reticle2]

    def __init__(self, *reticles):
        if not all(isinstance(r, self.value_type) for r in reticles):
            raise TypeError("Value should be a type of Reticle2 or None")
        super().__init__(reticles)

    def __setitem__(self, index, value):
        if not isinstance(value, self.value_type):
            raise TypeError("Value should be a type of Reticle2 or None")
        super().__setitem__(index, value)

    def __repr__(self):
        return f"<{self.__class__.__name__}({super().__repr__()})>"

    def sizeof(self, __type: Reticle2Type = PXL4ID):
        return sum(i.sizeof(__type) for i in set(self))


class Reticle2Container(RestrictedDict):
    allowed_keys = {'small', 'hold', 'base', 'lrf'}
    value_type = Optional[Reticle2ListContainer]

    @property
    def count(self):
        return sum(len(v) for v in self.values() if v is not None)

    def sizeof(self, __type: Reticle2Type = PXL4ID):
        return sum(v.sizeof(__type) for v in self.values() if v is not None)


if __name__ == "__main__":
    reticle = Reticle2Container(
        small=Reticle2ListContainer(
            Reticle2(
                Reticle2Frame()
            )
        )
    )
    print(reticle)
