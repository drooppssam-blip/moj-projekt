import sys
from PIL import Image, ImageDraw, ImageFont
# duży napis na pierwszą sekundę: biały tekst na czerwonym pasku, na środku kadru
text, out = sys.argv[1], sys.argv[2]
W, H = 1080, 1920
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
import os
size = int(os.environ.get('NAPIS_SIZE', '112'))
f = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', size)
step = int(size * 1.18)
lines = []; cur = ''
words = [] if '|' in text else text.split(' ')
if '|' in text: lines = [x.strip() for x in text.split('|')]
for w in words:
    t = (cur + ' ' + w).strip()
    if d.textlength(t, font=f) <= 960: cur = t
    else: lines.append(cur); cur = w
if cur: lines.append(cur)
lines = [l for l in lines if l.strip()]  # bez pustych linii (inaczej rysuje się mały pusty pasek)
y = int(os.environ.get('NAPIS_Y', '1150')) - (len(lines) * step) // 2
for l in lines:
    x = (W - d.textlength(l, font=f)) / 2
    bb = d.textbbox((x, y), l, font=f)
    d.rounded_rectangle((bb[0] - size // 4, bb[1] - size // 6, bb[2] + size // 4, bb[3] + size // 6), radius=size // 5, fill=(220, 38, 38, 245))
    d.text((x, y), l, font=f, fill=(255, 255, 255, 255))
    y += step
im.save(out)
