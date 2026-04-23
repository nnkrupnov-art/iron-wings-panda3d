#!/usr/bin/env python3
"""Create simple ICO icon for the game"""

import struct

# ICO Header: reserved(2), type(2), count(2)
ico_header = struct.pack('<HHH', 0, 1, 1)

# Directory Entry: width(1), height(1), colors(1), reserved(1), planes(2), bpp(2), size(4), offset(4)
width, height = 32, 32
bpp = 32
pixel_data = bytearray()
img_size = 40 + width * height * 4  # BMP header + pixels
dir_offset = 6 + 16  # header (6) + directory entry (16)
dir_entry = struct.pack('<BBBBHHII', width, height, 0, 0, 1, bpp, img_size, dir_offset)

# Pixel data (BGRA format, bottom-up)
for y in range(height - 1, -1, -1):
    for x in range(width):
        b, g, r, a = 80, 150, 180, 255
        cx, cy = width // 2, height // 2
        dy = abs(y - cy)
        dx = abs(x - cx)
        if 9 <= dy <= 13 and 4 <= dx <= 16:
            b, g, r = 30, 60, 60
        elif 4 <= dx <= 6 and 6 <= dy <= 25:
            b, g, r = 30, 60, 60
        elif 18 <= dy <= 21 and 11 <= dx <= 13:
            b, g, r = 30, 60, 60
        elif 24 <= dy <= 26 and 4 <= dx <= 6:
            b, g, r = 50, 50, 50
        pixel_data.extend([b, g, r, a])

# BMP Info Header (BITMAPINFOHEADER - 40 bytes)
bmp_info = struct.pack('<IiiHHII', 40, width, height, 1, bpp, 0, img_size - 40)
bmp_info += struct.pack('<iiII', 0, 0, 0, 0)

data = ico_header + dir_entry + bmp_info + bytes(pixel_data)

with open('icon.ico', 'wb') as f:
    f.write(data)

print(f'Created icon.ico ({len(data)} bytes)')
