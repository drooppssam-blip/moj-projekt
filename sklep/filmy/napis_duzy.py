import sys
from PIL import Image, ImageDraw, ImageFont
# duży napis na pierwszą sekundę: biały tekst na czerwonym pasku, na środku kadru
text, out = sys.argv[1], sys.argv[2]
W, H = 1080, 1920
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 112)
lines = []; cur = ''
words = [] if '|' in text else text.split(' ')
if '|' in text: lines = [x.strip() for x in text.split('|')]
for w in words:
    t = (cur + ' ' + w).strip()
    if d.textlength(t, font=f) <= 960: cur = t
    else: lines.append(cur); cur = w
if cur: lines.append(cur)
y = 1150 - (len(lines) * 132) // 2
for l in lines:
    x = (W - d.textlength(l, font=f)) / 2
    bb = d.textbbox((x, y), l, font=f)
    d.rounded_rectangle((bb[0] - 28, bb[1] - 18, bb[2] + 28, bb[3] + 18), radius=20, fill=(220, 38, 38, 245))
    d.text((x, y), l, font=f, fill=(255, 255, 255, 255))
    y += 132
im.save(out)
