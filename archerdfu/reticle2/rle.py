from typing import Literal

from PIL import Image

TByteorder = Literal["little", "big"]


def pack_record(x: int, y: int, q: int, *, byteorder: TByteorder = 'little') -> bytes:
    r = (x << 20) | (y << 10) | q
    return r.to_bytes(4, byteorder=byteorder)


def unpack_record(data: bytes, *, byteorder: TByteorder = 'little') -> tuple[int, int, int]:
    r = int.from_bytes(data, byteorder=byteorder)
    return (r >> 20) & 0xFFF, (r >> 10) & 0x3FF, r & 0x3FF


def _adjust_img_size(img: Image.Image, size: tuple[int, int] | list[int] = (640, 480)):
    if img.size == size:
        return img.copy()

    crop_width, crop_height = size
    width, height = img.size

    # If the image is smaller than the crop size, create a white background
    if width < crop_width or height < crop_height:
        new_img = Image.new("RGB", (crop_width, crop_height), "white")
        paste_x = (crop_width - width) // 2
        paste_y = (crop_height - height) // 2
        new_img.paste(img, (paste_x, paste_y))
        img = new_img  # Use the new padded image

    # Calculate cropping box
    left = (img.width - crop_width) // 2
    top = (img.height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height

    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))

    return cropped_img


def encode(img: Image.Image, size: tuple[int, int] | list[int] = (640, 480), threshold: int = 127):
    # Відкриваємо зображення
    img = img.convert('RGB')  # Перетворюємо в RGB, якщо зображення має інший формат
    img = _adjust_img_size(img, size)

    width, height = img.size
    pixels = img.load()

    buffer = b''

    for y in range(height):
        x = 0
        while x < width:
            color = pixels[x, y]
            intensity = sum(color) / 3  # Обчислюємо інтенсивність пікселя
            if intensity <= threshold:
                start_x = x  # Зберігаємо початкову позицію сегмента
                count = 1
                x += 1
                while x < width:
                    color = pixels[x, y]
                    intensity = sum(color) / 3
                    if intensity <= threshold:
                        count += 1
                        x += 1
                    else:
                        break
                # Додаємо сегмент з початковою координатою start_x
                buffer += pack_record(start_x, y, count)
            else:
                x += 1

    return img.size, buffer


def decode(buffer: bytes, size: tuple[int, int] | list[int] = (640, 480)) -> Image.Image:
    width, height, *_ = size
    img = Image.new('RGB', size, color='white')
    pixels = img.load()
    for n in range(0, len(buffer), 4):
        x, y, count = unpack_record(buffer[n:n + 4])
        for i in range(count):
            if 0 <= x + i < width and 0 <= y < height:
                pixels[x + i, y] = (0, 0, 0)  # Чорний піксель
    return img

# if __name__ == '__main__':
#     from construct import ByteSwapped, BitStruct, BitsInteger
#
#     ReticleData = ByteSwapped(BitStruct(
#         'x' / BitsInteger(12),
#         'y' / BitsInteger(10),
#         'q' / BitsInteger(10),
#     ))
#
#     # Використання функції
#     img = Image.open('../../assets/sample1.bmp')
#     # img.show()
#
#     size, buf = encode(img)
#
#     img = decode(buf, size)
#     # img.show()
#     img.save('../../assets/sample2.bmp')
#
#     img = Image.open('../../assets/sample2.bmp')
#     img.show()
#
#     size2, buf2 = encode(img)
#
#     assert buf == buf2
#
#     b1 = pack_record(1, 2, 3)
#     b2 = ReticleData.build(dict(x=1, y=2, q=3))
#     print(b1, b2)
#     c1 = unpack_record(b1)
#     c2 = ReticleData.parse(b2)
#     print(c1, c2)
