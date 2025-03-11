from dataclasses import dataclass
from copy import deepcopy


SQUARE = [[-1, -1, 3],
          [-1, 0, 1],
          [1, 0, 1],
          [-1, 1, 3]]

CROSS5 = [[0, -2, 1],
          [0, -1, 1],
          [-2, 0, 5],
          [0, 1, 1],
          [0, 2, 1]]

BIRD = [[0, 0, 1],
        [-1, 1, 1],
        [1, 1, 1],
        [-2, 2, 1],
        [2, 2, 1],
        [-3, 3, 1],
        [3, 3, 1]]

CROSS3 = [[0, -1, 1],
          [-1, 0, 3],
          [0, 1, 1]]

VLINE5 = [[0, -2, 1],
          [0, -1, 1],
          [0, 0, 1],
          [0, 1, 1],
          [0, 2, 1]]

NUMBER = {
    '0': [[-2, -3, 5],
        [-2, 3, 5],
        [-2, -2, 1],
        [-2, -1, 1],
        [-2, 0, 1],
        [-2, 1, 1],
        [-2, 2, 1],
        [2, -2, 1],
        [2, -1, 1],
        [2, 0, 1],
        [2, 1, 1],
        [2, 2, 1]],

    '1': [[-2, -3, 3],
        [-2, 3, 5],
        [0, -2, 1],
        [0, -1, 1],
        [0, 0, 1],
        [0, 1, 1],
        [0, 2, 1]],

    '2': [[-2, -3, 5],
        [2, -2, 1],
        [2, -1, 1],
        [-2, 0, 5],
        [-2, 1, 1],
        [-2, 2, 1],
        [-2, 3, 5]],

    '3': [[-2, -3, 5],
        [2, -2, 1],
        [2, -1, 1],
        [0, 0, 2],
        [2, 1, 1],
        [2, 2, 1],
        [-2, 3, 5]],

    '4': [[-2, -3, 1],
        [-2, -2, 1],
        [-2, -1, 1],
        [2, -3, 1],
        [2, -2, 1],
        [2, -1, 1],
        [-2, 0, 5],
        [2, 1, 1],
        [2, 2, 1]],

    '5': [[-2, -3, 5],
        [-2, -2, 1],
        [-2, -1, 1],
        [-2, 0, 5],
        [2, 1, 1],
        [2, 2, 1],
        [-2, 3, 5]],

    '6': [[-2, -3, 5],
        [-2, -2, 1],
        [-2, -1, 1],
        [-2, -0, 5],
        [-2, 1, 1],
        [-2, 2, 1],
        [2, 1, 1],
        [2, 2, 1],
        [-2, 3, 5]],

    '7': [[-2, -3, 5],
        # [-2, -2, 1],
        [2, -2, 1],
        [2, -1, 1],
        [1, 0, 1],
        [0, 1, 1],
        [0, 2, 1],
        [0, 3, 1]],

    '8': [[-2, -3, 5],
        [-2, -2, 1],
        [-2, -1, 1],
        [2, -2, 1],
        [2, -1, 1],
        [-1, 0, 3],
        [-2, 1, 1],
        [-2, 2, 1],
        [2, 1, 1],
        [2, 2, 1],
        [-2, 3, 5]],

    '9': [[-2, -3, 5],
        [-2, -2, 1],
        [-2, -1, 1],
        [-2, 0, 5],
        [2, -2, 1],
        [2, -1, 1],
        [2, 1, 1],
        [2, 2, 1],
        [-2, 3, 5]],
}

NUM = NUMBER
FONT_SIZE = 5
FONT_SPASING = 2


@dataclass
class Item:
    __slots__ = 'x', 'y', 'q'
    
    x: int
    y: int
    q: int
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.q
        

class Element:

    def __init__(self, mil, t):
        self.mil = mil
        self.t = [Item(*item) for item in t]

    def __repr__(self):
        return f'<({self.mil}, {len(self.t)})>'

    def append(self, other):
        if isinstance(other, Item):
            self.t.append(other)
        else:
            raise TypeError

    def __add__(self, other):
        if isinstance(other, (int, float)):
            for i in self.t:
                i.x += other
            return self
        elif isinstance(other, Element):
            for i in other.t:
                self.t.append(i)
            return self
        raise TypeError

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            for i in self.t:
                i.x -= other
            return self
        raise TypeError


El = Element
END_ITEM = Item(700, 1000, 0)

SMALL_RET = ((1, 230, 320), (1, 231, 320), (1, 232, 320), (1, 233, 320), (1, 234, 320), (1, 235, 320), (1, 236, 320),
             (1, 237, 320), (1, 238, 320), (1, 239, 320), (21, 240, 310), (1, 241, 320), (1, 242, 320), (1, 243, 320),
             (1, 244, 320), (1, 245, 320), (1, 246, 320), (1, 247, 320), (1, 248, 320), (1, 249, 320), (1, 250, 320))
SMALL_RET = tuple(
    i[::-1] for i in SMALL_RET
)


def _supersonic_row(distance):
    nums = str(distance // 100)
    num = El(-3, [])
    move = 0
    for i in nums[::-1]:
        num += El(-3, NUM[i]) - move
        move += FONT_SIZE + FONT_SPASING
    return num
        
def _subsonic_row(distance):
    nums = str(distance // 1)
    num = El(-5, [])
    move = 0
    for i in nums[::-1]:
        num += El(-2, NUM[i]) - move
        move += FONT_SIZE + FONT_SPASING
    return num

def create_row(distance, zero=100, subsonic=False):
    if distance == zero:
        return [El(x, VLINE5) for x in range(-5, 0)] + [El(0, BIRD)] + [El(x, VLINE5) for x in range(1, 6)]
    elif distance % 100 == 0:
        row = [El(-1, SQUARE), El(0, CROSS5), El(1, SQUARE)]
        if subsonic:
            num = _subsonic_row(distance)
        else:
            num = _supersonic_row(distance)   
        row.insert(0, num)
        return deepcopy(row)
    elif distance % 100 == 50:
        return [El(0, CROSS3)]

def create_hold_reticle(distances, zero, click, zoom=1, y_shift=9, subsonic=False):
    y = 0
    mil = 10000 / click * zoom
    img_data = []
    for d in distances:
        macro = []
        row = create_row(d, zero, subsonic)
        if row:
            macro.extend([
                Item(700, round(d / 10), 0),
                Item(700, 0, 0),
                Item(700, y, 0)
            ])
            for el in row:
                for it in el.t:
                    it.x += round(mil * el.mil) + 320
                    it.y += y + 240
                    macro.append(it)
            y += y_shift
        img_data = macro + img_data
    img_data.append(END_ITEM)
    return img_data
