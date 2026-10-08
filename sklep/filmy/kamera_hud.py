#!/usr/bin/env python3
"""Napisy w stylu kamery domowej, jedna klatka PNG na każdą sekundę (zegar tyka).
użycie: kamera_hud.py katalog liczba_sekund [HH:MM:SS start]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
out, n = sys.argv[1], int(sys.argv[2]); start = sys.argv[3] if len(sys.argv) > 3 else '03:12:07'
h, m, s = map(int, start.split(':'))
os.makedirs(out, exist_ok=True)
M = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
f, fs = ImageFont.truetype(M, 44), ImageFont.truetype(M, 34)
fw = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
def txt(d, xy, t, font, fill=(255, 255, 255, 235)):
    x, y = xy
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)): d.text((x + dx, y + dy), t, font=font, fill=(0, 0, 0, 180))
    d.text(xy, t, font=font, fill=fill)
for i in range(n):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tot = h * 3600 + m * 60 + s + i
    txt(d, (40, 40), '08.10.2026', f)
    txt(d, (40, 96), f'{tot // 3600 % 24:02d}:{tot // 60 % 60:02d}:{tot % 60:02d}', f)
    txt(d, (790, 40), 'CAM 2', f)
    txt(d, (790, 96), 'SALON', fs)
    if i % 2 == 0: d.ellipse((1000, 108, 1030, 138), fill=(230, 30, 30, 240))   # migająca kropka REC
    txt(d, (40, 1850), 'kocisparing.pl', fw, (255, 255, 255, 150))           # dyskretny znak marki
    im.save(f'{out}/h{i:02d}.png')
print('ok', n)
